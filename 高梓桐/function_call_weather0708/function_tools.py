import requests
import json
import logging as log


    


BAIDU_SEARCH = {
            "type": "function",
            "function": {
                "name": "baidu_search",
                "description": "根据用户提供信息通过互联网搜索引擎查询对应问题的信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "查询关键词"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    
WEATHER_SEARCH = {
            "type": "function",
            "function": {
                "name": "weather_search",
                "description": "获取某个城市的天气预报信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "查询城市"
                        }
                    },
                    "required": ["city"]
                }
            }
        }

def weather_search(city):
    log.info(f"weather_search: city={city}")
    
    # 基本参数配置
    apiUrl = 'http://apis.juhe.cn/simpleWeather/query'  # 接口请求URL
    apiKey = '137b61d3aaff9d6e2ec3875bd06059b3'  # 在个人中心->我的数据,接口名称上方查看

    # 接口请求入参配置
    requestParams = {
        'key': apiKey,
        'city': '苏州',
    }

    # 发起接口网络请求
    response = requests.get(apiUrl, params=requestParams)

    # 解析响应结果
    if response.status_code == 200:
        responseResult = response.json()
        # 网络请求成功。可依据业务逻辑和接口文档说明自行处理。
        return f'{responseResult["result"]}'
    else:
        # 网络异常等因素，解析结果异常。可依据业务逻辑自行处理。
        print('请求异常')



def baidu_search(query):

    log.info(f"baidu_search: query={query}")
    # 请求资源
    uri = "https://qianfan.baidubce.com/v2/ai_search"
    
    # 请求head信息
    heads = {
        "Content-Type": "application/json",
        "Authorization": "Bearer bce-v3/ALTAK-aXS6GMeLzciXvrMTO2XX0/6a0d19e55abe66a5b589acdc5c59d329ab17f30e"
    }

    # 发送请求
    response = requests.post(
        uri, 
        json={
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ]
        },
        headers=heads
    )
    
    result = json.loads(response.text)
    return f'{result["references"]}'
        
