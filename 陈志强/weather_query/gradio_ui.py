import gradio as gr
import function_tools
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

def update_model_name(model_input):
    # 根据选择的大模型平台更新模型名称
    return function_tools.MODEL_MAPPING[model_input]["model_name"]

def chatbot_interface(query, model_input, temperature, max_tokens):
    # 处理聊天请求
    config = function_tools.MODEL_MAPPING[model_input]
    
    client = OpenAI(
        base_url=os.environ[config["url"]],
        api_key=os.environ[config["key"]]  
    )
    
    tools = [function_tools.JUHE_WEATHER_SEARCH]
    messages = [
        {"role": "system", "content": "不需要要求用户补充问题,直接按问题调用tool"},
        {"role": "user", "content": query}
    ]
    
    response = client.chat.completions.create(
        model=config["model_name"],
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    # 处理工具调用
    if response.choices[0].message.tool_calls is not None:
        tool_call = response.choices[0].message.tool_calls[0]
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        invoke_fun = getattr(function_tools, function_name)
        result = invoke_fun(**function_args)
        
        messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": response.choices[0].message.tool_calls
        })
        messages.append({
            "role": "tool",
            "content": json.dumps(result),
            "tool_call_id": tool_call.id
        })
        
        response = client.chat.completions.create(
            model=config["model_name"],
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    
    return "未能获取有效响应"

if __name__ == "__main__":
    load_dotenv()
    
    with gr.Blocks() as demo:
        gr.Markdown("## 天气查询助手")
        with gr.Row():
            with gr.Column(scale=2):
                query = gr.Textbox(label="请输入", value="今天北京天气怎么样？", lines=3)
                submit_button = gr.Button("提交", variant="primary")
                text_output = gr.Textbox(label="模型回复", lines=6, interactive=False)
                with gr.Row():
                    example_btn1 = gr.Button("今天北京天气怎么样？")
                    example_btn2 = gr.Button("今天北京的空气质量如何？")
                    example_btn3 = gr.Button("未来几天北京的天气怎么样？")
            
            with gr.Column(scale=1):
                gr.Markdown("### 大模型平台")
                model_input = gr.Radio(
                    list(function_tools.MODEL_MAPPING.keys()),
                    label="",
                    value="Openai"
                )
                gr.Markdown("### 模型名称")
                model_name = gr.Textbox(
                    label="",
                    value=function_tools.MODEL_MAPPING["Openai"]["model_name"],
                    interactive=False
                )
                
                gr.Markdown("### 温度")
                temperature = gr.Slider(0, 1, value=0.8, step=0.1, label="")
                
                gr.Markdown("### 最大Token数")
                max_tokens = gr.Slider(128, 2048, value=512, step=1, label="")

        # 示例按钮点击事件
        def set_example_text(example):
            return example
        
        example_btn1.click(fn=set_example_text, inputs=gr.Textbox("今天北京天气怎么样？", visible=False), outputs=query)
        example_btn2.click(fn=set_example_text, inputs=gr.Textbox("今天北京的空气质量如何？", visible=False), outputs=query)
        example_btn3.click(fn=set_example_text, inputs=gr.Textbox("未来几天北京的天气怎么样？", visible=False), outputs=query)

        # 模型选择变化时更新模型名称
        model_input.change(
            fn=update_model_name,
            inputs=model_input,
            outputs=model_name
        )
        
        # 提交按钮点击事件
        submit_button.click(
            fn=chatbot_interface,
            inputs=[query, model_input, temperature, max_tokens],
            outputs=text_output
        )

    demo.launch()