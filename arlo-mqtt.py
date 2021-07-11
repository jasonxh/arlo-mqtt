#!/usr/bin/env python

import argparse
import logging
import os
import threading
import time
import typing as t

from arlo import Arlo

from arlo_homie import HomieArloBaseStation, HomieArloCamera


class ArloMqtt:
    log: logging.Logger
    report_interval: int
    report_thread: threading.Thread
    stop: threading.Event
    last_reported_ts: float
    arlo_user: str
    arlo_pass: str
    mqtt_settings: t.Dict[str, t.Any]

    arlo: Arlo
    arlo_bases: t.Dict[str, HomieArloBaseStation]
    arlo_cams: t.Dict[str, HomieArloCamera]

    def __init__(self, args: argparse.Namespace) -> None:
        self.log = logging.getLogger(type(self).__name__)
        if args.debug:
            self.log.setLevel(logging.DEBUG)

        self.report_interval = args.report_interval

        self.report_thread = threading.Thread(
            target=self.report_thread_fn)
        self.report_thread.daemon = True
        self.stop = threading.Event()
        self.last_reported_ts = time.time()

        self.arlo_user = args.arlo_user
        self.arlo_pass = args.arlo_pass

        self.mqtt_settings = {
            'MQTT_BROKER': args.broker,
            'MQTT_PORT': args.port,
            'MQTT_USERNAME': args.mqtt_user,
            'MQTT_PASSWORD': args.mqtt_pass,
        }

    def report_thread_fn(self) -> None:
        try:
            while True:
                self.report()
                self.last_reported_ts = time.time()

                if self.stop.wait(self.report_interval):
                    break
        except Exception:
            self.log.exception('Report thread failed')
        finally:
            self.log.info('Report thread stopped')
            self.stop.set()

    def run(self) -> None:
        self.log.info('Connecting to Arlo')
        self.arlo = Arlo(self.arlo_user, self.arlo_pass)
        self.arlo_bases = {}
        self.arlo_cams = {}

        self.report_thread.start()

        try:
            while True:
                if self.stop.wait(self.report_interval * 2):
                    break

                if time.time() - self.last_reported_ts > self.report_interval * 2:
                    self.log.error('Report timeout')
                    break
        finally:
            self.log.info('Main thread stopped')
            self.stop.set()

    def report(self) -> None:
        self.log.info('Reporting status')

        # Fetching devices and states from Arlo
        devices = [
            dev
            for dev in self.arlo.GetDevices() if dev['state'] != 'removed'
        ]

        bases = {
            dev['deviceId']: dev
            for dev in devices if dev['deviceType'] == 'basestation'
        }

        cams = {
            dev['deviceId']: dev
            for dev in devices if dev['deviceType'] == 'camera'
        }

        for mode in self.arlo.GetModesV2():
            id = mode['gatewayId']
            if id in bases:
                bases[id]['modeState'] = mode

        for base in bases.values():
            for state in self.arlo.GetCameraState(base)['properties']:
                id = state['serialNumber']
                if id in cams:
                    cams[id]['cameraState'] = state

        # Syncing devices and states to MQTT Homie
        for id, base in bases.items():
            if id not in self.arlo_bases:
                self.arlo_bases[id] = HomieArloBaseStation(
                    id=id,
                    name=base['deviceName'],
                    mqtt_settings=self.mqtt_settings,
                    arlo=self.arlo,
                    base_station=base,
                    log=self.log.getChild('homie'),
                )

            self.arlo_bases[id].node.active_modes = ','.join(
                base['modeState']['activeModes'])

        for id in [id for id in self.arlo_bases if id not in bases]:
            del self.arlo_bases[id]

        for id, cam in cams.items():
            if id not in self.arlo_cams:
                self.arlo_cams[id] = HomieArloCamera(
                    id=id,
                    name=cam['deviceName'],
                    mqtt_settings=self.mqtt_settings,
                    arlo=self.arlo,
                    base_station=bases[cam['parentId']],
                    log=self.log.getChild('homie'),
                )

            self.arlo_cams[id].node.privacy_active = cam['cameraState']['privacyActive']
            self.arlo_cams[id].node.battery_level = cam['cameraState']['batteryLevel']
            self.arlo_cams[id].node.charging_state = cam['cameraState']['chargingState']
            self.arlo_cams[id].node.connection_state = cam['cameraState']['connectionState']
            self.arlo_cams[id].node.signal_strength = cam['cameraState']['signalStrength']
            self.arlo_cams[id].node.last_image = cam['presignedLastImageUrl']

        for id in [id for id in self.arlo_cams if id not in cams]:
            del self.arlo_cams[id]


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
    parser.add_argument('-i', '--report-interval', default=600, type=int,
                        help='Interval in seconds between state refreshes. Defaults to 600.')

    group = parser.add_argument_group('Arlo')
    group.add_argument('--arlo-user', **_default_env('ARLO_USER'),
                       help='Arlo username. Can also be set via env ARLO_USER.')
    group.add_argument('--arlo-pass', **_default_env('ARLO_PASS'),
                       help='Arlo password. Can also be set via env ARLO_PASS.')

    group = parser.add_argument_group('MQTT')
    group.add_argument('--broker', default='localhost',
                       help='MQTT broker address. Defaults to localhost.')
    group.add_argument('--port', default=1883, type=int,
                       help='MQTT broker port. Defaults to 1883.')
    # group.add_argument('--tls', action='store_true',
    #                   help='Use TLS connection to MQTT broker.')
    group.add_argument('--mqtt-user', **_default_env('ARLO_MQTT_USER'),
                       help='MQTT username. Can also be set via env ARLO_MQTT_USER.')
    group.add_argument('--mqtt-pass', **_default_env('ARLO_MQTT_PASS'),
                       help='MQTT password. Can also be set via env ARLO_MQTT_PASS.')

    args = parser.parse_args()
    ArloMqtt(args).run()


if __name__ == "__main__":
    main()
