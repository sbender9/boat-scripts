#!/usr/bin/python

import time
import socket
import json
import sys
from subprocess import call
from pprint import pprint
from datetime import datetime, timedelta

HOST='localhost'
CANBOAT_CACHING_PORT=2597

device_tokens = [
  '<dfkjhdjsf sdfkjhhj dsfkhdsf ksdhfddsf dskfjhd sdfkhj dsfhkkj dsfkjhsd>',
    ]

last_alarm_times = {}

engine_pgn = '127489'
depth_pgn = '128267'
battery_status = '127508'
wind_pgn = '130306'
attitude_pgn = '127257'

excesive_attitute_alarm=3.0
excesive_wind_alarm = 20.0
high_wind_alarm = 10.0
shallow_depth_alarm = 8.0

status_bits = [ 'Check Engine',
                'Over Temperature',
                'Low Oil Pressure',
                'Low Oil Level',
                'Low Fuel Pressure',
                'Low System Voltage',
                'Low Coolant Level',
                'Water Flow',
                'Water in Fuel',
                'Charge Indicator',
                'Preheat Indicator',
                'High Boost Pressure',
                'Rev Limit Exceeded',
                'EGR System',
                'Throttle Position Sensor',
                'Emergency Stop Mode' ]
LOW_VOLTAGE = 5

def meters_to_feet(val):
    return val * 3.28084

def ms_to_knots(val):
    return val * 1.94384;

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

def find_field(dict, fname, match=None):

    for key in dict.keys():
        if key == 'description':
            continue
        if dict[key].has_key('fields'):
            fields = dict[key]['fields']
            
            if fields.has_key(fname):
                matched = 1
                if match:
                    for fn in match.keys():
                        if not fields.has_key(fn) or fields[fn] != match[fn]:
                            matched = 0
                if matched:
                    return fields[fname]
    return None

def get_bit(byteval,idx):
    return ((byteval&(1<<idx))!=0);

def make_alarm(title, body, type=None):
    alarm = {}
    alarm['title'] = title
    alarm['body'] = body
    if not type:
        type = title
    alarm['type'] = type

    return alarm

def check_engine_status(engine):
    alarms = []
    bits = int(find_field(engine, 'Discrete Status 1'))
    if bits:
        for idx in range(0,len(status_bits)-1):
            if get_bit(bits, idx):
                alarm = make_alarm('Engine Alarm', status_bits[idx],
                                   status_bits[idx])
                alarms.append(alarm)
                if idx == LOW_VOLTAGE and dict.has_key(battery_status):
                    bs = dict[battery_status];
                    starter = find_field(bs, 'Voltage', {'Battery Instance':0})
                    house = find_field(bs, 'Voltage', {'Battery Instance':1})
                    alarm['body'] = '%s: House %0.2f, Starter %0.2f' % (status_bits[idx], starter, house)
    return alarms

def check_depth(depth):
    mdepth = find_field(depth, "Depth")
    offset = find_field(depth, "Offset")

    mdepth = mdepth + offset
    fdepth = meters_to_feet(mdepth)

    if fdepth < shallow_depth_alarm:
        return [make_alarm('Shallow Depth', 'Depth is %0.2f ft' 
                           % fdepth)]
    return []

def check_wind(dict):
    speed = find_field(dict, 'Wind Speed')
    kspeed = ms_to_knots(speed)
    #print 'wind', kspeed
    if kspeed > excesive_wind_alarm:
        return [make_alarm('Excessive Wind', 'Wind Speed is %0.2f kts' 
                           % kspeed, 'excessive_wind')]
    elif kspeed > high_wind_alarm:
        return [make_alarm('High Wind', 'Wind Speed is %0.2f kts' 
                           % kspeed, 'high_wind')]
    return []

def check_attitude(dict):
    roll = find_field(dict, 'Roll')
    pitch = find_field(dict, 'Pitch')

    alarms = []

    if roll > excesive_attitute_alarm:
        alarms.append(make_alarm('Excessive Attitude', 'Roll is %0.2f' % roll,
                                 'Roll'))

    if pitch > excesive_attitute_alarm:
        alarms.append(make_alarm('Excessive Attitude', 'Pitch is %0.2f' 
                                 % pitch, 'Pitch'))

    return alarms

if __name__ == '__main__':
    while 1:
        messages = load_json(HOST, CANBOAT_CACHING_PORT)
        dict = json.loads(messages)

        alarms = []

        if dict.has_key(engine_pgn):
            engine = dict[engine_pgn]
            alarms.extend(check_engine_status(engine))

        if dict.has_key(depth_pgn):
            alarms.extend(check_depth(dict[depth_pgn]))

        if dict.has_key(wind_pgn):
            alarms.extend(check_wind(dict[wind_pgn]))

        if dict.has_key(attitude_pgn):
            alarms.extend(check_attitude(dict[attitude_pgn]))

        for alarm in alarms:
            type = alarm['type']
            if last_alarm_times.has_key(type):
                last_time = last_alarm_times[type]
                hour_from = last_time + timedelta(minutes=15)
                if datetime.now() < hour_from:
                    continue

            for token in device_tokens:
                command = ['ruby', 'push.rb', '--title', alarm['title'], 
                           '--body', alarm['body'], '--token', token]
                call(command)
                
            last_alarm_times[type] = datetime.now()
            pprint(datetime.now())
            pprint(alarm)

        sys.stdout.flush()
        time.sleep(60)
