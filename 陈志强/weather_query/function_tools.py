import requests
import logging as log

JUHE_WEATHER_SEARCH = {
            "type": "function",
            "function": {
                "name": "juhe_weather_search",
                "description": "获取某个城市或地区的天气预报信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "城市名称"
                        }
                    },
                    "required": ["city"]
                }
            }
        }

# 模型映射配置
MODEL_MAPPING = {
    "Openai": {
        "key": "OPENAI_API_KEY",
        "url": "OPENAI_API_BASE",
        "model_name": "gpt-3.5-turbo"
    },
    "Zhipuhi": {
        "key": "ZHIPU_API_KEY",
        "url": "ZHIPU_API_BASE",
        "model_name": "glm-4-flash"
    },
    "DeepSeek": {
        "key": "DEEPSEEK_API_KEY",
        "url": "DEEPSEEK_API_BASE",
        "model_name": "deepseek-chat"
    }
}

# 天气查询工具(聚合数据)
def juhe_weather_search(city):
    log.info(f'juhe_weather_search: city={city}')
    # 1213-根据城市查询天气 - 代码参考（根据实际业务情况修改）
    # 基本参数配置
    apiUrl = 'http://apis.juhe.cn/simpleWeather/query'  # 接口请求URL
    apiKey = '2f6ef59bf87df21e22aa961ce57bc07c'  # 在个人中心->我的数据,接口名称上方查看

    # 接口请求入参配置
    requestParams = {
        'key': apiKey,
        'city': city,
    }

    # 发起接口网络请求
    response = requests.get(apiUrl, params=requestParams)

    # # 打印响应结果
    # if response.status_code == 200:
    #     responseResult = response.json()
    #     # 网络请求成功。可依据业务逻辑和接口文档说明自行处理。
    #     print(responseResult)
    # else:
    #     # 网络异常等因素，解析结果异常。可依据业务逻辑自行处理。
    #     print('请求异常')

    #返回响应结果
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': '请求异常', 'status_code': response.status_code}