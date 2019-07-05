#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import requests
import ssl
import socket
import json
import package.include.mylib as mylib


ID='77918'
TOKEN='b345e40b0070c53f89e3a521d70c7967'

domain_name = '16302.com'			# 主域名 名称
record_name = "bgs" 				# 子域名 名称
token       = ID+','+TOKEN
domain_id   = 67684523

def post(url, post_data={} ):
    r = mylib.mylib().curl_post(url, post_data)
    return r

#获取公网IP
def getremoteip():
    sock = socket.create_connection(('ns1.dnspod.net', 6666))
    ip = sock.recv(16)
    sock.close()
    return ip

#获取子域名记录 ID 和 IP
def get_record_id(name, domain_id, token):
    post_data = {"login_token":token,"format":"json","domain_id":domain_id}
    url = "https://dnsapi.cn/Record.List"
    data = post(url, post_data);
    data = json.loads(data)
    for value in data["records"]:
        if (value['name'] == name):
            return {'record_id':value['id'], 'record_ip':value['value']}

# 获取域名ID
def get_domain_id(domain_name, token):
    url = "https://dnsapi.cn/Domain.List"
    post_data = {"login_token":token,"format":"json"}
    data = post(url, post_data)
    data = json.loads(data)
    for value in data["domains"]:
        if (value['punycode'] == domain_name):
            print('domain_id = '+ value['id']+ ";\n\n")

# 设置IP
def modip(ip, id, record_name, domain_id, token):
    url = "https://dnsapi.cn/Record.Modify";
    post_data = {"login_token":token,"format":"json","domain_id":domain_id,"record_id":id,"value":ip,"record_type":"A","record_line_id":0,"sub_domain":record_name}
    data = post(url, post_data)
    data = json.loads(data)
    if (data['status']['code'] == "1"):
        print("设备新IP成功！");
    else:
        print(data['status']['message'])

def main():
    value = get_record_id(record_name, domain_id, token);
    ip = getremoteip();		# 获取公网IP

    if (value):
        if (value['record_ip'] and str('b'+"'"+value['record_ip']+"'")!=str(ip)):
            modip(ip, value['record_id'], record_name, domain_id, token);
        else:
            print("同样的IP，无需更新："+value['record_ip']);

if __name__ == '__main__':
    main()
