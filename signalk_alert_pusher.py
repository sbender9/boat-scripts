#!/usr/bin/python

import time
import socket
import json
import sys
from subprocess import call
from pprint import pprint
from datetime import datetime, timedelta
import httplib
import traceback

#HOST='192.168.1.200'
HOST='localhost'
PORT=3000

device_tokens = [
  '<dfkjhdjsf sdfkjhhj dsfkhdsf ksdhfddsf dskfjhd sdfkhj dsfhkkj dsfkjhsd>',
    ]

last_alarm_times = {}

depth_path = 'environment.depth.belowTransducer.value'
offset_path = 'environment.depth.surfaceToTransducer.value'
battery_status_path = 'electrical.batteries.%d.capacity.stateOfCharge.value'
wind_path = 'environment.wind.speedApparent.value'
roll_path = 'navigation.attitude.roll'
pitch_path = 'navigation.attitude.pitch'

excesive_attitute_alarm = 3.0
excesive_wind_alarm = 20.0
high_wind_alarm = 10.0
shallow_depth_alarm = 8.0

notification_data = {
    'engineOverTemperature': {
        'paths': ['propulsion.port.temperature.value'],
        'msg': 'The engine temperature is %s'
        },
    'engineLowOilPressure': {
        'paths': [ 'propulsion.port.oilPressure.value' ],
        'msg': 'The engine oil pressure is %s'
        },
    'lowSystemVoltage': {
        'paths': [ 'electrical.batteries.0.capacity.stateOfCharge.value',
                   'electrical.batteries.1.capacity.stateOfCharge.value' ],
        'msg': 'A battery voltage is low. Starter bank is %0.2f. House bank is %0.2f'
        }
}


def meters_to_feet(val):
    return val * 3.28084

def ms_to_knots(val):
    return val * 1.94384;

def load_json(host, port):
    conn = httplib.HTTPConnection(host, port)
    conn.request("GET", "/signalk/v1/api/")
    res = conn.getresponse()
    if res.status != 200:
        print "Error connecting to %s:%d: %d %s" % (host, port, res.status, res.reason)
        return None
    else:
        return res.read()

def get_from_path(element, json):
    return reduce(lambda d, key: d[key], element.split('.'), json)

def make_alarm(title, body, type=None):
    alarm = {}
    alarm['title'] = title
    alarm['body'] = body
    if not type:
        type = title
    alarm['type'] = type

    return alarm

def check_depth(vessel):
    mdepth = get_from_path(depth_path, vessel)
    offset = get_from_path(offset_path, vessel)

    mdepth = mdepth + offset
    fdepth = meters_to_feet(mdepth)

    #print 'depth', fdepth

    if fdepth < shallow_depth_alarm:
        return [make_alarm('Shallow Depth', 'Depth is %0.2f ft' 
                           % fdepth)]
    return []

def check_wind(vessel):
    speed = get_from_path(wind_path, vessel)
    kspeed = ms_to_knots(speed)
    #print 'wind', kspeed
    if kspeed > excesive_wind_alarm:
        return [make_alarm('Excessive Wind', 'Wind Speed is %0.2f kts' 
                           % kspeed, 'excessive_wind')]
    elif kspeed > high_wind_alarm:
        return [make_alarm('High Wind', 'Wind Speed is %0.2f kts' 
                           % kspeed, 'high_wind')]
    return []

def check_attitude(vessel):
    roll = get_from_path(roll_path, vessel)
    pitch = get_from_path(pitch_path, vessel)

    #print 'attitude', pitch, roll
    alarms = []

    if roll > excesive_attitute_alarm:
        alarms.append(make_alarm('Excessive Attitude', 'Roll is %0.2f' % roll,
                                 'Roll'))

    if pitch > excesive_attitute_alarm:
        alarms.append(make_alarm('Excessive Attitude', 'Pitch is %0.2f' 
                                 % pitch, 'Pitch'))

    return alarms

def check_for_notifications(vessel):
    alarms = []
    if vessel.has_key('notifications'):
        notifications = vessel['notifications']

        if notifications and len(notifications):
            #print notifications
            for key in notifications.keys():
                #pprint(notifications[key])
                msg = notifications[key]['message']
                alarm = make_alarm(msg, msg, key)

                if notification_data.has_key(key):
                    nd = notification_data[key]
                    paths = nd['paths']
                    vals = ()
                    for path in paths:
                        vals = vals + (get_from_path(path, vessel),)

                    alarm['body'] = nd['msg'] % vals

                alarms.append(alarm)

    return alarms

def check_for_alarms(vessel):
    alarms = []

    alarms.extend(check_for_notifications(vessel))

    alarms.extend(check_depth(vessel))

    alarms.extend(check_wind(vessel))

    alarms.extend(check_attitude(vessel))

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
            #print command

        last_alarm_times[type] = datetime.now()
        print time.asctime(time.localtime(time.time()))
        pprint(alarm)


if __name__ == '__main__':
    while 1:
        try:
            messages = load_json(HOST, PORT)

            if messages:
                dict = json.loads(messages)

                vessels = dict['vessels']
                if vessels and len(vessels):
                    vessel = vessels[vessels.keys()[0]];
                    if vessel:
                        check_for_alarms(vessel)
        except:
            print("Unexpected error:", sys.exc_info())
            traceback.print_exc()

        sys.stdout.flush()
        time.sleep(60)
