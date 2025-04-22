import socket
import json
from zrh_wifi_html import html
import gc
from micropython import const
import machine
from zrh_wifi_config import WifiConfigFile
import asyncio

# 配置常量
HOST = const('0.0.0.0')
PORT = const(80)
LISTEN_NUM = const(5)
RECV_LENGTH = const(1024)
RESPONSE = const('HTTP/1.0 200 OK\r\nContent-type:')
RN = const('\r\n\r\n')
CONTENT_TYPE = {
    'json': RESPONSE + 'application/json' + RN,
    'html': RESPONSE + 'text/html' + RN
}


class ZrhSocket:
    """原生实现web http服务,不使用第三方包，占用内存更小,8266可以使用"""

    def __init__(self):
        """初始化服务器套接字"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((HOST, PORT))
            self.socket.listen(LISTEN_NUM)
            print(f"Server started on {HOST}:{PORT}")
        except Exception as e:
            print(f"Error initializing server: {e}")
            self.socket = None

    def handle_client(self, conn, addr):
        """处理客户端请求"""
        try:
            data = conn.recv(RECV_LENGTH)
            if not data:
                print("No data received")
                return

            # 解析请求
            data_arr = data.decode().split("\r\n")
            request_line = data_arr[0]

            # 提取请求方法和 URL
            request_method, url, _ = request_line.split(' ')

            # 解析路径和查询参数
            path, query_params = self.parse_url(url)

            # 根据路径返回响应
            if path == '/wifi':
                response = self.wifi_html_page()
            elif path == '/save_wifi_config':
                response = self.save_wifi_config(query_params)
            else:
                response = self.default_response(
                    request_method, path, query_params)

            # conn.send(response.encode())
            conn.sendall(response.encode('utf-8'))
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            conn.close()
            gc.collect()

    def parse_url(self, url):
        """解析 URL,返回路径和查询参数"""
        if '?' in url:
            path, query_string = url.split('?', 1)
            query_params = {}
            for param in query_string.split('&'):
                key, value = param.split('=')
                query_params[key] = value
            return path, query_params
        else:
            return url, {}

    def wifi_html_page(self):
        """返回 WiFi 配置页面的 HTML 内容"""
        return CONTENT_TYPE['html'] + html

    def default_response(self, method, path, query_params):
        """构造默认 JSON 响应"""
        res = {
            "status": 200,
            "method": method,
            "path": path,
            "query": query_params
        }
        return CONTENT_TYPE['json'] + json.dumps(res)

    def save_wifi_config(self, params):
        wifiConfigFile = WifiConfigFile()
        wifiConfigFile.save(params["ssid"], params["password"])
        res = {
            "status": 200,
            "isSuccess": True,
        }
        asyncio.create_task(self._reboot())
        return CONTENT_TYPE['json'] + json.dumps(res)

    async def _reboot(self):
        await asyncio.sleep(1)
        print("reset device!!!")
        machine.reset()

    def start(self):
        """启动服务器"""
        if not self.socket:
            print('Server not initialized')
            return

        try:
            while True:
                conn, addr = self.socket.accept()
                self.handle_client(conn, addr)
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            if self.socket:
                self.socket.close()
                gc.collect()
