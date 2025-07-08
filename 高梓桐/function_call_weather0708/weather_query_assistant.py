import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv
from zhipuai import ZhipuAI  # Ensure you have the ZhipuAI library installed
import os
import json
import function_tools  # 假设 function_tools 中包含天气查询工具 WEATHER_QUERY

# 加载环境变量
load_dotenv()

# 初始化 OpenAI 客户端（若后续扩展其他平台，可在此处补充对应初始化逻辑）
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_API_BASE")
)

# 初始化智谱客户端
zhipu_client = ZhipuAI(
    api_key=os.environ["ZHIPU_API_KEY"],
    base_url=os.environ["ZHIPU_API_BASE"]
)

# 初始化百炼客户端
# bailian_client = BailianAI(
#     api_key=os.environ.get("BAILIAN_API_KEY"),
#     base_url=os.environ.get("BAILIAN_API_BASE")
# )

# 定义工具
tools = [
    function_tools.WEATHER_SEARCH  # 假设 function_tools 中定义了 WEATHER_SEARCH 工具
]

# 定义支持的模型列表
OPENAI_MODELS = ["gpt-3.5-turbo", "gpt-4"]
ZHIPUAI_MODELS = ["glm-4-flash", "glm-4"]
BAILIAN_MODELS = ["bailian-model-1", "bailian-model-2"]

# 定义 Gradio 接口的处理函数，增加模型相关参数接收
def weather_query(prompt, model_platform, model_name, temperature, max_tokens):
    # 输入验证
    if model_platform == "openai" and model_name not in OPENAI_MODELS:
        return f"OpenAI 平台不支持 {model_name} 模型，请选择 {', '.join(OPENAI_MODELS)} 中的模型。"
    elif model_platform == "ZhipuAI" and model_name not in ZHIPUAI_MODELS:
        return f"智谱 AI 平台不支持 {model_name} 模型，请选择 {', '.join(ZHIPUAI_MODELS)} 中的模型。"
    elif model_platform == "Bailian" and model_name not in BAILIAN_MODELS:
        return f"百炼平台不支持 {model_name} 模型，请选择 {', '.join(BAILIAN_MODELS)} 中的模型。"

    # 根据选择的大模型平台，可扩展对应逻辑，这里先简单处理，默认用 OpenAI 逻辑示例
    # 构造消息
    messages = [
        {"role": "system", "content": "你是一个天气查询助手，可以通过工具查询天气信息。"},
        {"role": "user", "content": prompt}
    ]

    # 调用对应大模型 API，这里先以 OpenAI 为例，若选其他平台需补充逻辑
    if model_platform == "openai":
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=temperature,
            max_tokens=max_tokens
        )
    # 若有其他平台（如 ZhipuAI、Bailian ），补充对应调用逻辑
    elif model_platform == "ZhipuAI":
        zhipu_messages = [{"role": msg["role"], "content": msg["content"]} for msg in messages]
        zhipu_request = {
            "model": model_name,
            "messages": zhipu_messages,
            "parameters": {
                "functions": [tool["function"] for tool in tools],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        }
        try:
            response = zhipu_client.chat.completions.create(**zhipu_request)
            # 处理智谱 AI 响应
            if response.code == 200:
                response = response.data
            else:
                return f"智谱 AI 请求失败，错误码: {response.code}, 错误信息: {response.msg}"
        except Exception as e:
            return f"调用智谱 AI 时发生错误: {str(e)}"
    # 在 weather_query 中注释百炼逻辑
    elif model_platform == "Bailian":
        return "暂未实现 Bailian 平台对接，敬请期待"
    else:
        return "未识别的大模型平台，请检查选择"

    # 处理工具调用（和之前逻辑类似，若不同平台工具调用差异大，需针对性调整）
    while hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls is not None:
        messages.append(response.choices[0].message)
        for tool_call in response.choices[0].message.tool_calls:
            args = tool_call.function.arguments
            args = json.loads(args)
            function_name = tool_call.function.name
            import function_tools
            invoke_fun = getattr(function_tools, function_name)
            result = invoke_fun(**args)
            messages.append({
                "role": "tool",
                "content": f"{json.dumps(result)}",
                "tool_call_id": tool_call.id
            })
        # 再次调用 API，这里同样需注意不同平台的适配，先以 OpenAI 为例
        if model_platform == "openai":
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                tools=tools,
                temperature=temperature,
                max_tokens=max_tokens
            )
        elif model_platform == "ZhipuAI":
            zhipu_messages = [{"role": msg["role"], "content": msg["content"]} for msg in messages]
            zhipu_request = {
                "model": model_name,
                "messages": zhipu_messages,
                "parameters": {
                    "functions": [tool["function"] for tool in tools],
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            }
            try:
                response = zhipu_client.chat.completions.create(**zhipu_request)
                if response.code == 200:
                    response = response.data
                else:
                    return f"智谱 AI 请求失败，错误码: {response.code}, 错误信息: {response.msg}"
            except Exception as e:
                return f"调用智谱 AI 时发生错误: {str(e)}"
        else:
            # 其他平台暂简单处理，实际需完善
            break

    return response.choices[0].message.content

# 创建 Gradio 界面
with gr.Blocks() as demo:
    gr.Markdown("## 天气查询助手")
    with gr.Row():
        with gr.Column(scale=2):
            input_text = gr.Textbox(label="请输入", value="今天北京天气怎么样？", lines=3)
            submit_btn = gr.Button("提交", variant="primary")
            output_text = gr.Textbox(label="模型回复", lines=3, interactive=False)
            with gr.Row():
                example_btn1 = gr.Button("今天北京天气怎么样？")
                example_btn2 = gr.Button("今天北京的空气质量如何？")
                example_btn3 = gr.Button("未来几天北京的天气怎么样？")
        with gr.Column(scale=1):
            gr.Markdown("### 大模型平台")
            model_platform = gr.Radio(["openai", "ZhipuAI", "Bailian"], label="", value="openai")
            gr.Markdown("### 模型名称")
            model_name = gr.Dropdown(choices=["gpt-3.5-turbo", "gpt-4"], label="", value="gpt-3.5-turbo")
            
            gr.Markdown("### 温度")
            temperature_slider = gr.Slider(minimum=0.0, maximum=1.0, value=0.7, step=0.1, label="Temperature")

            gr.Markdown("### 最大 Token 数")
            max_tokens_slider = gr.Slider(minimum=1, maximum=2048, value=512, step=1, label="Max Tokens")

            # 根据平台动态更新模型名称选项
            def update_model_choices(platform):
                if platform == "openai":
                    return gr.update(choices=["gpt-3.5-turbo", "gpt-4"], value="gpt-3.5-turbo")
                elif platform == "ZhipuAI":
                    return gr.update(choices=["glm-4-flash", "glm-4"], value="glm-4-flash")
                elif platform == "Bailian":
                    return gr.update(choices=["bailian-model-1", "bailian-model-2"], value="bailian-model-1")

            model_platform.change(fn=update_model_choices, inputs=[model_platform], outputs=[model_name])

    # 示例按钮点击事件，将示例文本填入输入框
    def set_example_text():
        return "今天北京天气怎么样？"

    example_btn1.click(fn=set_example_text, inputs=[], outputs=input_text)
    example_btn2.click(fn=set_example_text, inputs=[], outputs=input_text)
    example_btn3.click(fn=set_example_text, inputs=[], outputs=input_text)

    # 提交按钮点击事件，传入更多参数
    submit_btn.click(
        fn=weather_query,
        inputs=[input_text, model_platform, model_name, temperature_slider, max_tokens_slider],
        outputs=output_text
    )

# 启动 Gradio 应用
if __name__ == "__main__":
    demo.launch()