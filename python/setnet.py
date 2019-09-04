# -*- coding: UTF-8 -*-
import socket
import signal
import sys,os,re,time
from multiprocessing import Process
from package.base import Base,log                       #基本类
import package.mysocket as mysocket                     #发送websocket
import bin.html.wificore as wificore

# HTTP服务器
class HTTPServer(Base):

    def __init__(self):
        self.response_ret = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("", 80))
        self.server_socket.listen(128)
        self.is_stop = False

        # 设置根目录
        self.HTML_ROOT_DIR = os.path.join(self.config['root_path'], 'bin/html')
        sys.path.insert(1, self.HTML_ROOT_DIR)

    #动态网页最终处理状态
    def response_state(self, retjson ):
        if type(retjson) is dict:
            self.response_ret = retjson

    def start(self):
        print('HTTP服务已启动')
        while True:
            if self.is_stop:return
            client_socket, client_address = self.server_socket.accept()
            #print("[%s, %s]用户连接上了" % client_address)
            handle_client_process = Process(target=self.handle_client, args=(client_socket,))
            handle_client_process.start()
            client_socket.close()

    def stop(self):
        self.is_stop = True
        print('HTTP服务已停止')

    def start_response(self, status, headers):
        response_headers = "HTTP/1.1 " + status + "\r\n"
        for header in headers:
            response_headers += "%s: %s\r\n" % header

        self.response_headers = response_headers

    def handle_client(self, client_socket):
        """
        处理客户端请求
        """
        # 获取客户端请求数据
        request_data = client_socket.recv(1024)
        #print("request data:", request_data)
        request_lines = request_data.splitlines()
        for line in request_lines:
            #print(line)
            pass

        # 解析请求报文
        #GET /getwifilist.py?_=1563551930521 HTTP/1.1
        request_start_line = request_lines[0]
        request_start_line = request_start_line.decode("utf-8")
        request_start_line = request_start_line.strip("b'")
        #print( request_start_line )

        # 提取用户请求的文件名及请求方法
        file_name = re.match(r"\w+\s+(/[^\s]*) ", request_start_line).group(1)
        method    = re.match(r"(\w+)\s+/[^\s]*\s", request_start_line).group(1)

        print('提取原文件名:', file_name,method )

        if file_name == 'favicon.ico':
            return

        if "/" == file_name:
            file_name = "/index.html"
        else:
            file_name = re.match(r"(/[\w|\.]+)\??", file_name).group(1)

        print('解析后文件名:', file_name,method )

        request_data = ''
        if request_lines[-1]:
            request_data = str(request_lines[-1])

        # 处理动态文件
        if file_name.endswith(".py"):
            try:
                m = __import__(file_name[1:-3])
            except Exception:
                self.response_headers = "HTTP/1.1 404 Not Found\r\n"
                response_body = "not found"
            else:
                env = {
                    "PATH_INFO": file_name,
                    "METHOD": method,
                    "DATA": request_data
                }
                response_body = m.application(env, self.start_response, self.response_state )

            response = self.response_headers + "\r\n" + response_body
        # 处理静态文件
        else:
            # 打开文件，读取内容
            #print('打开文件:', self.HTML_ROOT_DIR + file_name )
            try:
                file = open(self.HTML_ROOT_DIR + file_name, "rb")
            except IOError:
                response_start_line = "HTTP/1.1 404 Not Found\r\n"
                response_headers = "Server: My server\r\n"
                response_body = "The file is not found!"
            else:
                file_data = file.read()
                file.close()

                # 构造响应数据
                response_start_line = "HTTP/1.1 200 OK\r\n"
                response_headers = "Server: My server\r\n"
                response_body = file_data.decode("utf-8")

            response = response_start_line + response_headers + "\r\n" + response_body
            #print("response data:", response)

        # 向客户端返回响应数据
        client_socket.send(bytes(response, "utf-8"))

        # 关闭客户端连接
        client_socket.close()


"""配网类"""
class Setnet(Base):
    def __init__(self):
        self.wifico = wificore.Wificore()
        #前后端通讯
        self.sw = mysocket.Mysocket()

        self.http_server = HTTPServer()
        self.http_server.response_state = self.response_state

        self.http_server_pid = 0

        self.neterrri = 0       #错误尝试次数

        self.voice = os.path.join(self.config['root_path'],'bin/voice')

        self.buzhou = {
            'scann' : True      #扫描二维码语音提示
        }

    #循环检测网络是否配置成功
    def loop_testnet(self):
        st = self.wifico.test_network()
        if st == True:
            self.sw.send({"t":"setnet","netstatus": 1})
            os.system('aplay '+ os.path.join(self.voice, '配网成功.wav'))
            self.open_url('index.html')
            self.http_server.is_stop = True
            return True
        else:
            self.sw.send({"t":"setnet","netstatus": 0})
            self.neterrri += 1
            if self.neterrri > 60:
                self.wifico.is_exit = False
                os.system('aplay '+ os.path.join(self.voice, '验证网络失败.wav'))
                self.main()
                return False
            else:
                time.sleep(1)
                return self.loop_testnet()


    #动态网页执行后的返回结果
    def response_state(self, ret_json):
        if type(ret_json) is dict:
            if ret_json['env']['PATH_INFO'] == '/setwifi.py':
                self.open_url('server_netstatus.html')
                #print('保存的子pid', self.http_server_pid )
                self.http_server.stop()
                os.system('sudo kill -9 '+ str(self.http_server_pid) )
                os.popen('aplay '+ os.path.join(self.voice, '验证网络配置.wav'))
                self.loop_testnet()

    #开启httpserver服务器
    def start_httpserver(self):
        self.http_server_pid = os.getpid()
        #print('子'*100, self.http_server_pid )
        self.http_server.start()

    #打开服务端网页
    def open_url(self, ourl):
        navjson = {
            'event': 'self',
            'url': ourl
        }
        self.sw.send_nav( navjson )

    #检测是否有手机连接到AP
    def query_client(self):
        st = self.wifico.query_ap_clients()
        if st == 'ERROR':return     #出错了，跳出查询
        print('query_client', st )
        send_json = {
            "t":"setnet",
            "client": st
        }
        try:
            self.sw.send(send_json)
            if st==1 and self.buzhou['scann']:
                os.popen('aplay '+ os.path.join(self.voice, '扫描二维码.wav'))
                self.buzhou['scann'] = False
        except:pass

        time.sleep(1)
        self.query_client()


    #开始配置
    def start_config(self):
        print('进入这里了')
        Process(target=self.start_httpserver).start()
        time.sleep(1)
        self.open_url('server.html')
        time.sleep(2)
        os.popen('aplay '+ os.path.join(self.voice, '连接无线网络.wav'))
        self.query_client()

    #停止配网
    def stop_config(self):
        os.system('sudo kill -9 '+ str(self.http_server_pid) )
        self.wifico.stop_ap()

    #开始配网操作
    def main(self):
        os.popen('aplay '+ os.path.join(self.voice, '开始配置网络.wav'))
        st = self.wifico.init_network()
        self.wifico.start_ap_success = self.start_config
        if st == True:
            self.wifico.start_ap()
            self.wifico.query_ap()

if __name__ == "__main__":
    Setnet().main()