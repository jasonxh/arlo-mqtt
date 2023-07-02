import argparse
import json
import logging
import os
import typing as t

from arlo_mqtt.core import ArloMqtt


def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def _default_env(env_var: str) -> t.Dict[str, t.Any]:
        if env_var in os.environ:
            return {'default': os.environ[env_var]}
        else:
            return {'required': True}

    parser = argparse.ArgumentParser(
        description='A simple bridge between Arlo and MQTT.')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debug logging.')

    group = parser.add_argument_group('Arlo')
    group.add_argument('--arlo-user', **_default_env('ARLO_USER'),
                       help='Arlo username. Can also be set via env ARLO_USER.')
    group.add_argument('--arlo-pass', **_default_env('ARLO_PASS'),
                       help='Arlo password. Can also be set via env ARLO_PASS.')
    group.add_argument('--arlo-extras-json', default=os.environ.get('ARLO_EXTRAS_JSON', '{}'),
                       help='Pyaarlo extra options in JSON format. E.g., you can specify 2FA options here. Can also be set via env ARLO_EXTRAS_JSON.')

    group = parser.add_argument_group('MQTT')
    group.add_argument('--broker', default='localhost',
                       help='MQTT broker address. Defaults to localhost.')
    group.add_argument('--port', default=1883, type=int,
                       help='MQTT broker port. Defaults to 1883.')
    group.add_argument('--mqtt-user', **_default_env('ARLO_MQTT_USER'),
                       help='MQTT username. Can also be set via env ARLO_MQTT_USER.')
    group.add_argument('--mqtt-pass', **_default_env('ARLO_MQTT_PASS'),
                       help='MQTT password. Can also be set via env ARLO_MQTT_PASS.')

    args = parser.parse_args()
    ArloMqtt(
        arlo_user=args.arlo_user,
        arlo_pass=args.arlo_pass,
        mqtt_broker=args.broker,
        mqtt_port=args.port,
        mqtt_user=args.mqtt_user,
        mqtt_pass=args.mqtt_pass,
        debug=args.debug,
        pyaarlo_extras=json.loads(args.arlo_extras_json),
    ).run()
