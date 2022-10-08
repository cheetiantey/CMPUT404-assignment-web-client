#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data): 
        """Extracts the response code of the HTTP response (e.g., 200, 404, etc)
        
        Args:
            data: the HTTP response
        
        Returns: 
            The HTTP response code
        """
        data = data.split(" ")
        # print(f"data is: {data}")
        http_response_code = int(data[1]) if len(data) > 1 else 404
        return http_response_code

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def encode_args(self, args):
        """Encode the GET/POST arguments into a properly formatted query parameter

        Args:
            args: POST argument
        
        Returns:
            A query paramter to be used in the body of the GET/POST request
        """
        arr = []
        for key, val in args.items():
            _arr = ""
            _arr += key + "="
            for c in val:
                if c == "\n":
                    _arr += "%0A"
                elif c == "\r":
                    _arr += "%0D"
                else:
                    _arr += c
            arr.append(_arr)
        print("arr is: ", arr)
        return "&".join(arr)

    def GET(self, url, args=None):
        # print(f"url is: {url}")
        code = 500
        body = ""
        
        # print("GET part")
        url = urllib.parse.urlparse(url)
        
        port_number = url.port if url.port else 80 # Default prot for HTTP is 80 while HTTPs is 443
        try:
            self.connect(url.hostname, port_number)
        except:
            code = 404
            self.close()
            return HTTPResponse(code, body)
        
        url_path = url.path if url.path else "/"

        http_header = f"GET {url_path} HTTP/1.1\r\nHost:{url.hostname}\r\nAccept: */*\r\nConnection: close\r\n\r\n"
        self.sendall(http_header)

        body = self.recvall(self.socket)

        self.close()
        code = self.get_code(body)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        print(f"url is: {url}")
        code = 500
        body = ""

        url = urllib.parse.urlparse(url)
        port_number = url.port if url.port else 80 # Default prot for HTTP is 80 while HTTPs is 443
        try:
            self.connect(url.hostname, port_number)
        except:
            code = 404
            self.close()
            print("404 Error***")
            return HTTPResponse(code, body)

        url_path = url.path if url.path else "/"

        http_header = f"POST {url_path} HTTP/1.1\r\nHost:{url.hostname}\r\nAccept: */*"
        # args_len = len(args) if args else 0
        print("original args is:     ", args)
        print("args_to_str(args) is: ", self.encode_args(args)) if args else None
        args_len = len(self.encode_args(args)) if args else 0
        http_header += "\r\nContent-length: " + str(args_len)
        if args:
            http_header += "\r\nContent-Type : application/x-www-form-urlencoded"
            http_header += "\r\n\r\n" + self.encode_args(args)

        http_header += "\r\nConnection: close\r\n\r\n"
        # http_header += "\r\n\r\n"
        self.sendall(http_header)
        body = self.recvall(self.socket)
        # print(body)
        self.close()
        code = self.get_code(body)
        
        bodytest = body.split("\r\n\r\n")
        bodytest = bodytest[1] if len(bodytest) > 1 else None
        return HTTPResponse(code, bodytest)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
