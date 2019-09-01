import wificore as wificore

def application(env, start_response, response_state):
    status = "200 OK"
    headers = [("Content-Type", "application/json")]
    start_response(status, headers)

    print( env )

    if type(env['DATA']) is dict:
        set_json = env['DATA']

        wifico = wificore.Wificore()
        #初始化网络状态
        wifico.config_wifi(set_json)

        return '{"code":"0000"}'
    else:
        return '{"code":"9999","msg":"数据格式错误！"}'