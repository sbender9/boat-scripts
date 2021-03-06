## Synopsis

Custom scripts that run on the raspberry pi on my 1980 Catalina 30 (Wilhelm)

## Scripts

- canboat_alert_pusher.py - uses the [CANboat](https://github.com/canboat/canboat) caching port to push apple notifications for n2k Engine Alerts and custom wind, depth and attitude
- signalk_alert_pusher.py - uses the [SignalK](http://signalk.org) api to push apple notifications for n2k Engine Alerts and custom wind, depth and attitude
- canboat_http_interface.py - provides an http interface for caching and streaming for the local [CANboat](https://github.com/canboat/canboat) server - usefull to provide access to CANboat data when plain tcp sockets are not available (like on the APple Watch)
- push.rb - used by the pusher script to do the actual call to the Apple API's

## Requirements For Push Scripts
- [houston](https://github.com/nomad/houston) - used by push.rb to call the Apple push notifications API
- A custom iOS app that is setup and registered to get push notifications
- Edit the pusher scripts to add the device_tokens
- Edit push.rb with the path to your Apple push certificate 

## Execution

I run these via the /etc/rc.local:

```
/home/sbender/source/canboat_http.py > /dev/null 2>&1 &
/home/sbender/source/signalk_alert_pusher.py > /tmp/alerts.log 2>&1 &
```

