#!/usr/bin/python
import time
import argparse

calibrate_depth = '%s,3,126208,%s,%s,11,01,0b,f5,01,f8,01,03,%02x,%02x,ff,ff'

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help(sys.stderr)
        sys.exit(2)

def format_n2k_date():
    return time.strftime('%Y-%m-%dT%H:%M.%SZ', time.gmtime())


parser = argparse.ArgumentParser(description='WilhelmSK Server')
parser.add_argument('--dst', action='store', dest='dst',
                      help='airmar device id',required=True)
parser.add_argument('--value', action='store', dest='value',
                    help='transducer offset',required=True,type=float)  

args = parser.parse_args()
  
val = args.value

val = int(val * 1000)

print calibrate_depth % (format_n2k_date(), '0', args.dst, (val & 0xff),
                         ((val >> 8) & 0xff))


