#!/usr/bin/python

import time
import BaseHTTPServer
import socket
from urlparse import urlparse, parse_qs


HOST_NAME = '' # ALL interfaces
PORT_NUMBER = 2596 # Maybe set this to 9000.

def load_json(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    chunks = []

    while 1:
        chunk = s.recv(1000)
        if chunk == '':
            break
        chunks.append(chunk)

    fdata = ''.join(chunks)

    return fdata

def stream_json(self, host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    try:
        while 1:
            chunk = s.recv(1000)
            self.wfile.write(chunk)
    except:
        s.close()

    return 

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        """Respond to a GET request."""
        query_components = parse_qs(urlparse(s.path).query)
        streaming = 0
        if query_components.has_key('streaming'):
            str = query_components["streaming"][0]
            if str == 'true':
                streaming = 1

        if streaming == 0:
            s.send_response(200)
            s.send_header("Content-type", "text/json")
            s.end_headers()

            s.wfile.write(load_json('localhost', 2597))
        else:
            stream_json(s, 'localhost', 2598)


        
if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
