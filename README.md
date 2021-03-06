# arlo-mqtt
[![Build Status](https://travis-ci.org/jasonxh/arlo-mqtt.svg?branch=master)](https://travis-ci.org/jasonxh/arlo-mqtt)

A simple bridge between Arlo and MQTT.
Follows [Homie v3.0.1](https://homieiot.github.io/specification/spec-core-v3_0_1/) convention in exposing devices in MQTT.
Based on the Arlo python module from [jeffreydwalter/arlo](https://github.com/jeffreydwalter/arlo) and Homie3 python module from [mjcumming/HomieV3](https://github.com/mjcumming/HomieV3).

# Usage
```
usage: arlo-mqtt.py [-h] [-d] [-i REPORT_INTERVAL] [--arlo-user ARLO_USER]
                    [--arlo-pass ARLO_PASS] [--broker BROKER] [--port PORT]
                    [--mqtt-user MQTT_USER] [--mqtt-pass MQTT_PASS]

A simple bridge between Arlo and MQTT.

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           Enable debug logging.
  -i REPORT_INTERVAL, --report-interval REPORT_INTERVAL
                        Interval in seconds between state refreshes. Defaults
                        to 600.

Arlo:
  --arlo-user ARLO_USER
                        Arlo username. Can also be set via env ARLO_USER.
  --arlo-pass ARLO_PASS
                        Arlo password. Can also be set via env ARLO_PASS.

MQTT:
  --broker BROKER       MQTT broker address. Defaults to localhost.
  --port PORT           MQTT broker port. Defaults to 1883.
  --mqtt-user MQTT_USER
                        MQTT username. Can also be set via env ARLO_MQTT_USER.
  --mqtt-pass MQTT_PASS
                        MQTT password. Can also be set via env ARLO_MQTT_PASS.
```

# Docker
```
docker run --rm -it jasonxh/arlo-mqtt [args]
```

# MQTT Topic Structure
TODO
