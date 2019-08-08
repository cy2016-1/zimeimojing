import wificore as wificore

def application(env, start_response, response_state):
    status = "200 OK"
    headers = [("Content-Type", "application/json")]
    start_response(status, headers)

    request_data = ''
    if env['DATA']:
        request_data = env['DATA']

    post_data = {}
    if env['METHOD'] == 'POST':
        entry = str(request_data)
        entry = entry.strip("b'")
        if type(entry) is str:
            item = entry.split('&')
            for x in item:
                xitem = x.split('=')
                if xitem:
                    post_data[ str(xitem[0]) ] = str(xitem[1])

    if len(post_data) > 0:
        wifico = wificore.Wificore()
        #初始化网络状态
        wifico.config_wifi(post_data)

    ret_json = '{"code":"0000"}'
    response_json = {
        'env': env,
        'return': ret_json
    }
    response_state(response_json)

    return ret_json