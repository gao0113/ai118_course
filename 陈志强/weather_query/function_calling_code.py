import function_tools
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

if __name__ == "__main__":
    load_dotenv()

    # # 查询天气
    # city = "北京"
    # weather_data = function_tools.juhe_weather_search(city)

    # # OpenAI润色
    # if 'error' in weather_data:
    #     print(f"获取天气失败: {weather_data['error']}")
    # else:
    #     client = OpenAI(
    #         base_url=os.environ["OPENAI_API_BASE"],
    #         api_key=os.environ["OPENAI_API_KEY"],
    #     )

    #     response = client.chat.completions.create(
    #         model="gpt-4o-mini",
    #         messages=[
    #             {"role": "user", "content": f"以下内容是{city}的天气数据,请根据用户的问题输出合适的内容：{str(weather_data)}"}
    #         ],
    #     )
    #     print(response.choices[0].message.content)

    client = OpenAI(
        base_url=os.environ["OPENAI_API_BASE"],
        api_key=os.environ["OPENAI_API_KEY"]  
    )

    tools = [
        function_tools.JUHE_WEATHER_SEARCH
    ]

    messages = [
        {"role": "system", "content": "不需要要求用户补充问题,直接按问题调用tool"},
        {"role": "user", "content": "北京今天温度怎么样"}
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    # 处理工具调用
    if response.choices[0].message.tool_calls is not None:
        tool_call = response.choices[0].message.tool_calls[0]
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)


        # 外部模块动态获取并调用函数
        invoke_fun = getattr(function_tools, function_name)
        result = invoke_fun(**function_args)

        # 更新消息历史
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
            model="gpt-3.5-turbo",
            messages=messages
        )
        print(response.choices[0].message.content)