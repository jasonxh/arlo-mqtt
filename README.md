# arlo-mqtt
A simple bridge between Arlo and MQTT.
Based on the Arlo python module from [jeffreydwalter/arlo](https://github.com/jeffreydwalter/arlo).

# Usage
```
usage: arlo-mqtt.py [-h] [-d] [-i REPORT_INTERVAL] [--arlo-user ARLO_USER]
                    [--arlo-pass ARLO_PASS] [--broker BROKER] [--port PORT]
                    [--tls] [--mqtt-user MQTT_USER] [--mqtt-pass MQTT_PASS]
                    [--topic-root TOPIC_ROOT]

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
  --tls                 Use TLS connection to MQTT broker.
  --mqtt-user MQTT_USER
                        MQTT username. Can also be set via env ARLO_MQTT_USER.
  --mqtt-pass MQTT_PASS
                        MQTT password. Can also be set via env ARLO_MQTT_PASS.
  --topic-root TOPIC_ROOT
                        MQTT topic root. Defaults to arlo.
```

# Docker
```
docker run --rm -it jasonxh/arlo-mqtt [args]
```

# MQTT Topic Structure
TODO
