#!/usr/bin/python

import pexpect
import sys
import time
import traceback
import json
import time

char_read_res = 'Characteristic value/descriptor: .*? \r'

sleep_amount=0.2
def_timeout=5

device_state_map= {
    0: 'not charging',
    2: 'other',
    3: 'charging bulk',
    4: 'charging absorption',
    5: 'charging float'
    }

def read_char(child, hdl):
    time.sleep(sleep_amount)
    child.sendline('char-read-hnd %s' % hdl)
    res = child.expect(char_read_res, timeout=def_timeout)
    child.expect('.*\[LE\]> ')
    return res

def write_req(child, hdl, val):
    time.sleep(sleep_amount)
    child.sendline('char-write-req %s %s' % (hdl, val))
    child.expect('Characteristic value was written successfully', timeout=def_timeout)
    child.expect('.*\[LE\]> ')
    return

def write_cmd(child, hdl, val):
    time.sleep(sleep_amount)
    child.sendline('char-write-cmd %s %s' % (hdl, val))
    child.expect('.*\[LE\]> ', timeout=def_timeout)
    return

def decode_int16(b1, b2):
    return int('%s%s' % (b2, b1), 16)

def decode_int32(b1, b2, b3, b4):
    return int('%s%s%s%s' % (b4, b3, b2, b1), 16)

def decode_int8(b1):
    return int(b1, 16)

def connect_and_read():
    child = pexpect.spawn('gatttool -t random -b FB:22:A0:D3:29:E8 -I --sec-level=high')
    #child.logfile = sys.stdout
    child.logfile = open('/tmp/victron.out', 'wa')
    sys.stderr.write('Started at %s\n' % time.asctime(time.localtime(time.time())))
    child.expect('.*\[LE\]>')
    child.sendline('connect')
    child.expect('Connection successful', timeout=5)

    child.sendline('sec-level high')
    # child.sendline('char-write-req 0x0020 0100')

    read_char(child, '0x001f')
    read_char(child, '0x0014')
    read_char(child, '0x001b')
    read_char(child, '0x0017')
    read_char(child, '0x001c')
    read_char(child, '0x001f')
    read_char(child, '0x0020')
    read_char(child, '0x0023')
    read_char(child, '0x0026')
    write_req(child, '0x0020', '0100')
    write_req(child, '0x0023', '0100')
    write_req(child, '0x0026', '0100')
    write_cmd(child, '0x001f', 'fa80ff')
    write_cmd(child, '0x001f', 'f980')
    write_cmd(child, '0x0022', '01')
    write_cmd(child, '0x001f', 'f901')
    write_cmd(child, '0x0022', '0300')
    write_cmd(child, '0x0025', '0301030305008119010c05018119010005038119')
    write_cmd(child, '0x0025', '0100050381181805038119010c05038119034e05')
    write_cmd(child, '0x0025', '038119edad05038119eda8050381190201050381')
    write_cmd(child, '0x0022', '19ed8f05038119ed8d05038119edbb')

    done = 0
    while not done:
        child.expect('value: .*? \r')
        vals = child.match.group(0)[7:].strip().split()

        if len(vals) < 7:
            continue

        id = "%s%s" % (vals[3], vals[4])
        id = id.lower()

        if id == 'edd7': # Charger current (A)
            key = 'electrical.chargers.victron.current'
            value = decode_int16(vals[6], vals[7])
            value = value / 10.0
        elif id == 'edbb': # Panel voltage (V)
            key = 'electrical.chargers.victron.panelVoltage'
            value = decode_int16(vals[6], vals[7])
            value = value / 100.0
        elif id == 'ed8d': # Bat Voltage? (V)
            key = 'electrical.chargers.victron.batteryVoltage'
            value = decode_int16(vals[6], vals[7])
            value = value / 100.0
        elif id == 'edbc': # Panel Power (W)
            key = 'electrical.chargers.victron.panelPower'
            value = decode_int32(vals[6], vals[7], vals[8], vals[9])
            value = value / 100.0
        elif id == '0200': # Device mode (0 or 4 == charger off, 1=charger on)
            key = 'electrical.chargers.victron.state'
            value = decode_int8(vals[6])
            if value == 0 or value == 4:
                value = 'off'
            else:
                value = 'on'
        elif id == '0201': # Device state
            key = 'electrical.chargers.victron.mode'
            value = decode_int8(vals[6])
            if device_state_map.has_key(value):
                value = device_state_map[value]
            else:
                value = 'unknown'
        else: 
            continue

        delta = {
            "updates": [
                {
                    "source": {
                        "label": "victron_1"
                    },
                    "values": [
                        {
                            "path": key,
                            "value": value
                        }
                    ]
                }
            ]
        }
        print json.dumps(delta)
        #print '%s: ' % key, value

    child.sendline('diconnect')
    child.sendline('quit')

if __name__ == '__main__':
    while 1:
        try:
            connect_and_read()
        except:
            #sys.stderr.write("Unexpected error: ")
            #print sys.exc_info()
            traceback.print_exc(sys.stderr)
            sys.stderr.write('error, sleepeing\n')
            time.sleep(5)
