#!/usr/bin/python3
import os
import importlib
import sys
import json
import re
import gc
import socket
from urllib import parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from multiprocessing import Process

from MsgProcess import MsgType as Msg_Type

#-------------------------------------------------------------------------------

class ServerException(Exception):
    '''服务器内部错误'''
    pass

#-------------------------------------------------------------------------------

class base_case(object):
    '''条件处理基类'''

    def handle_file(self, handler, full_path):
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            handler.send_content(content, handler.mimetype)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(full_path, msg)
            handler.handle_error(msg)

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        assert False, 'Not implemented.'

    def act(self, handler):
        assert False, 'Not implemented.'

#-------------------------------------------------------------------------------

class case_no_file(base_case):
    '''文件或目录不存在'''

    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise ServerException("'{0}' not found".format(handler.path))

#-------------------------------------------------------------------------------

class case_cgi_file(base_case):
    '''可执行脚本'''

    def run_cgi(self, handler):
        basename = os.path.splitext(os.path.basename(handler.package_path))[0]
        dirname  = os.path.dirname(handler.package_path)

        root_package = str(dirname).replace(r"/",".")
        root_package = root_package.strip('.')

        module = root_package+'.'+basename
        if module in sys.modules.keys():
            # 模块已经存在
            package = sys.modules[module]
            importlib.reload(package)
        else:
            package = importlib.import_module(r'.'+basename, package=root_package)

        moduleClass = getattr(package, basename)
        process = moduleClass(handler)

        data = process.main()
        del package,moduleClass,process
        gc.collect()

        mimetype = handler.mimetype
        status = 200
        handler.send_content(data.encode("utf-8"), mimetype, status)

    def test(self, handler):
        return os.path.isfile(handler.full_path) and handler.full_path.endswith('.py')

    def act(self, handler):
        self.run_cgi(handler)

#-------------------------------------------------------------------------------

class case_existing_file(base_case):
    '''文件存在的情况'''

    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        self.handle_file(handler, handler.full_path)

#-------------------------------------------------------------------------------

class case_directory_index_file(base_case):
    '''在根路径下返回主页文件'''

    def test(self, handler):
        return os.path.isdir(handler.full_path) and os.path.isfile(self.index_path(handler))

    def act(self, handler):
        self.handle_file(handler, self.index_path(handler))

#-------------------------------------------------------------------------------

class case_always_fail(base_case):
    '''默认处理'''

    def test(self, handler):
        return True

    def act(self, handler):
        raise ServerException("Unknown object '{0}'".format(handler.path))

#-------------------------------------------------------------------------------
#===============================================================================

class RequestInit():
    ''' 请求初始化类，所有具体操作需继承此类，基本已封装好常用的常量和变量 '''

    def __init__(self, handler):
        self.mimetype = handler.mimetype
        self.command = handler.command

        if self.command=='OPTIONS':
            handler.send_content('', self.mimetype, 200)
            return

        self._OPTIONS = handler.OPTIONS
        self._POST = handler.POST
        self._GET = handler.GET

        self.handler = handler

    # 发送字典类型的消息
    def __send_dict(self, dictobj):
        template = {"MsgType": '', "Receiver": ''}
        if len(template.keys() & dictobj.keys()) != 2:
            return '发送参数格式有误'
        else:
            Sender = 'WebServer'
            if 'Sender' in dictobj.keys(): Sender = dictobj['Sender']
            Data = ''
            if 'Data' in dictobj.keys(): Data = dictobj['Data']
            message = {"MsgType": dictobj['MsgType'], "Receiver": dictobj['Receiver'], "Data": Data, "Sender": Sender}
            return self.handler.Sock.sendall(json.dumps(message).encode())


    # 与消息队列通信的函数
    def send(self, MsgType, Receiver=None, Data=None, Sender=None):
        if isinstance(MsgType, dict):
            # 如果是字典则不考虑后面的参数
            return self.__send_dict(MsgType)
        elif isinstance(MsgType, str):
            if not hasattr(Msg_Type, str(MsgType)):
                # 不是消息类型，先按JSON字符串处理
                try:
                    dictobj = json.loads(MsgType)
                    # 继续进行格式判断
                    return self.__send_dict(dictobj)
                except:
                    # 按一般字符串处理，默认发送到控制中心
                    message = {"MsgType": "Text", "Receiver": "ControlCenter", "Data": MsgType, "Sender": "WebServer"}
                    return self.handler.Sock.sendall(json.dumps(message).encode())
            elif Receiver==None:
                return '接收者（Receiver）参数不能为空'
            else:
                if Sender==None:Sender = "WebServer"
                if Data==None:Data = ''
                # 是消息类型写法
                message = {"MsgType": MsgType, "Receiver": Receiver, "Data": Data, "Sender": Sender}
                return self.handler.Sock.sendall(json.dumps(message).encode())

    def main(self):
        data = '感谢使用自美人工智能系统'
        return data

#===============================================================================
#-------------------------------------------------------------------------------

class RequestHandler(BaseHTTPRequestHandler):
    ''' 请求处理器 '''

    System_Root = os.path.dirname(os.path.abspath(__file__))
    Http_Root = os.path.join(System_Root, 'webroot')

    OPTIONS = {}
    GET = {}
    POST = {}

    IP_Port = ('127.0.0.1', 8183)
    Sock = socket.socket()     # 创建套接字

    '''
    请求路径合法则返回相应处理
    否则返回错误页面
    '''
    Cases = [case_no_file(),
             case_cgi_file(),
             case_existing_file(),
             case_directory_index_file(),
             case_always_fail()]

    # 错误页面模板
    Error_Page = """\
<html>
<head>
<meta charset="UTF-8">
<meta http-equiv="content-type" content="text/html; charset=utf-8">
</head>
<body>
<h1>访问错误 {path}</h1>
<p>{msg}</p>
</body>
</html>
"""

    Mimedic = [
        ('.html', 'text/html'),
        ('.htm', 'text/html'),
        ('.py', 'text/html'),
        ('.js', 'application/javascript'),
        ('.css', 'text/css'),
        ('.json', 'application/json'),
        ('.png', 'image/png'),
        ('.jpg', 'image/jpeg'),
        ('.gif', 'image/gif'),
        ('.svg', 'image/svg+xml'),
        ('.txt', 'text/plain'),
        ('.avi', 'video/x-msvideo')
    ]

    # 拆分web请求参数
    def __parse_parse_qs(self, query):
        argv_dict = {}
        for item in query.split('&'):
            if item.find("=") != -1:
                item_tab = item.split('=')
                argv_dict[item_tab[0]] = item_tab[1]
        return argv_dict

    # 处理身份验证
    def do_OPTIONS(self):
        result = parse.urlparse(self.path)
        self.path  = re.sub(r'^\/{2,}', "/",result.path)
        if result.query:
            self.OPTIONS = self.__parse_parse_qs(result.query)
        self.handle_request()

    # 处理GET请求
    def do_GET(self):
        result = parse.urlparse(self.path)
        self.path  = re.sub(r'^\/{2,}', "/",result.path)
        if result.query:
            self.GET = self.__parse_parse_qs(result.query)
        self.handle_request()

    # 处理POST请求
    def do_POST(self):
        result = parse.urlparse(self.path)
        self.path  = re.sub(r'^\/{2,}', "/",result.path)
        if result.query:
            self.GET = self.__parse_parse_qs(result.query)

        req_datas = self.rfile.read(int(self.headers['content-length'])) #重点在此步!
        query = req_datas.decode()

        query_dict = {}
        if len(query)>0:
            try:
                if query.find("=") != -1:
                    for item in query.split('&'):
                        if item.find("=") != -1:
                            item_tab = item.split('=')
                            query_dict[item_tab[0]] = item_tab[1]
                else:
                    query_dict.update( json.loads(query) )
            except:
                pass

        self.POST = query_dict

        self.handle_request()

    def handle_request(self):
        try:
            self.Sock.getpeername()
        except:
            try:
                self.Sock.connect(self.IP_Port)
            except Exception as msg:
                pass

        try:
            # 得到完整的请求路径
            if (re.search( r'^/plugin/', self.path, re.M|re.I)):
                self.package_path = os.path.join('/plugin', re.sub(r'^/', '',self.path,1) )
                HttpRoot = self.System_Root
            else:
                self.package_path = os.path.join('/webroot', re.sub(r'^/', '',self.path,1) )
                HttpRoot = self.Http_Root

            self.full_path = HttpRoot + self.path

            self.mimetype = ''
            filename, fileext = os.path.splitext(self.full_path)
            for e in self.Mimedic:
                if e[0] == fileext:
                    self.mimetype = e[1]
            del filename,fileext

            # 遍历所有的情况并处理
            for case in self.Cases:
                if case.test(self):
                    case.act(self)
                    break

        # 处理异常
        except Exception as msg:
            self.handle_error(msg)


    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content.encode("utf-8"), self.mimetype, 404)

    # 发送数据到客户端
    def send_content(self, content, mimetype='', status=200):
        self.send_response(status)

        if mimetype != '':
            self.send_header("Content-type", mimetype)
        self.send_header("Content-Length", str(len(content)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "X-Token")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

        self.end_headers()
        self.wfile.write(content)

#-------------------------------------------------------------------------------
class WebServer():
    '''HTTP服务器类'''

    def start(self):
        serverAddress = ('0.0.0.0', 8088)
        server = HTTPServer(serverAddress, RequestHandler)
        server.serve_forever()

    # 开始运行
    def Run(self, argv=''):
        if argv.lower() != 'debug':
            sys.stderr = open(os.devnull, 'w')      # http.server 使用stderr.write写日志。故转发到空设备屏蔽之
        p = Process(target=self.start)
        p.start()


if __name__ == '__main__':
    argv = ''
    if len(sys.argv) > 1:
        argv = sys.argv[1]
    # Web服务器
    sys.path.append(os.getcwd())

    webser = WebServer()
    webser.Run(argv)
