# arlo-mqtt
[![CI](https://github.com/jasonxh/arlo-mqtt/actions/workflows/ci.yaml/badge.svg?event=push)](https://github.com/jasonxh/arlo-mqtt/actions/workflows/ci.yaml)

A simple bridge between Arlo and MQTT.
Follows [Homie v4.0.0](https://homieiot.github.io/specification/spec-core-v4_0_0/) convention in exposing devices in MQTT.
Based on the Arlo python module from [twrecked/pyaarlo](https://github.com/twrecked/pyaarlo) and Homie4 python module from [mjcumming/Homie4](https://github.com/mjcumming/homie4).

# Usage
```
usage: arlo-mqtt [-h] [-d] [--arlo-user ARLO_USER] [--arlo-pass ARLO_PASS] [--arlo-extras-json ARLO_EXTRAS_JSON]
                 [--broker BROKER] [--port PORT] [--mqtt-user MQTT_USER] [--mqtt-pass MQTT_PASS]

A simple bridge between Arlo and MQTT.

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           Enable debug logging.

Arlo:
  --arlo-user ARLO_USER
                        Arlo username. Can also be set via env ARLO_USER.
  --arlo-pass ARLO_PASS
                        Arlo password. Can also be set via env ARLO_PASS.
  --arlo-extras-json ARLO_EXTRAS_JSON
                        Pyaarlo extra options in JSON format. E.g., you can specify 2FA options here. Can also be
                        set via env ARLO_EXTRAS_JSON.

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
