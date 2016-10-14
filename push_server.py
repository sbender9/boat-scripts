#!/usr/bin/python

import time
import BaseHTTPServer
import socket
import json
from pprint import pprint
from urlparse import urlparse, parse_qs


HOST_NAME = '' # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 3120 
devices_file = '/home/sbender/source/registerd_devices.json'

def read_devices():
    f = open(devices_file)
    dict = json.loads(f.read())
    f.close()
    return dict

def save_devices(devices):
    f = open(devices_file, "w")
    f.write(json.dumps(devices, sort_keys=True, indent=2))
    f.close()

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        """Respond to a GET request."""
        parsed = urlparse(s.path)
        if s.path == '/pushsupport':
            s.send_response(200)
            #s.send_header("Content-type", "text/json")
            s.end_headers()
        else:
            s.send_response(404)
            s.end_headers()
    def do_POST(s):
        parsed = urlparse(s.path)
        if s.path == '/register_device':
            data = s.rfile.read(int(s.headers['Content-Length']))
            dict = json.loads(data)
            devices = read_devices()
            devices[dict['id']] = dict
            save_devices(devices)
            s.send_response(200)
            s.end_headers()
        elif s.path == '/unregister_device':
            data = s.rfile.read(int(s.headers['Content-Length']))
            dict = json.loads(data)
            devices = read_devices()
            if devices.has_key(dict['id']):
                del devices[dict['id']]
            save_devices(devices)
            s.send_response(200)
            s.end_headers()            
        else:
            s.send_response(404)
            s.end_headers()                                                
            
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
