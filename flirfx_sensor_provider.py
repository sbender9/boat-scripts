#!/usr/bin/python

import requests
import logging
import time
import socket
import json

FLIRFX_IP='192.168.2.76'
FLIRFX_PASSWORD='xxxxxxx'

SEND_IP='127.0.0.1'
SEND_PORT=5151

TEMPERATURE_PATH='environment.inside.temperature'
HUMIDITY_PATH='environment.inside.humidity'

r = requests.post('http://%s/API/1.0/ChiconyCameraLogin' % FLIRFX_IP, data = '{ "password" : "%s" }' % FLIRFX_PASSWORD )

session = r.cookies['Session']

cookies = dict(Session=session)

#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while 1:
    r = requests.post('http://%s/API/1.1/CameraStatus' % FLIRFX_IP, cookies=cookies, data = '{ "getCameraStatus" : [ "humidity", "temperature"] }' )
    res = r.json()
    temp_units = res['temperature']['tempUnits']
    temp_value = res['temperature']['tempValue']
    humidity_value = res['humidity']['humidityLevel']

    if temp_units == 'F':
        temp_value = (temp_value + 459.67) * (5.0/9.0);
    elif temp_units == 'C':
        temp_value = temp_value + 273.15;

    delta = {
        "updates": [
            {
                "source": {
                    "label": "flirfx:%s" % FLIRFX_IP
                },
                "values": [
                    {
                        "path": TEMPERATURE_PATH,
                        "value": temp_value
                    },
                    {
                        "path": HUMIDITY_PATH,
                        "value": humidity_value
                    }
                ]
            }
        ]
    }
    print json.dumps(delta)
    #sock.sendto(json.dumps(delta) + "\n", (SEND_IP, SEND_PORT))
    time.sleep(5)


#Debug:
# try:
#     import http.client as http_client
# except ImportError:
#     import httplib as http_client
# http_client.HTTPConnection.debuglevel = 1

# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True
