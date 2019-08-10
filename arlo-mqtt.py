#!/usr/bin/env python3

import argparse
import json
import logging
import paho.mqtt.client as mqtt
import os
import sys
import threading
import time

from arlo import Arlo


class ArloMqtt:
    def __init__(self, args):
        self.log = logging.getLogger(type(self).__name__)
        if args.debug:
            self.log.setLevel(logging.DEBUG)

        self.report_interval = args.report_interval
        self.topic_root = args.topic_root

        self.report_thread = threading.Thread(target=self.report_thread_fn, daemon=True)
        self.arlo_event_thread = threading.Thread(target=self.arlo_event_thread_fn, daemon=True)
        self.stop = threading.Event()
        self.last_reported_ts = time.time()

        self.log.info('Connecting to Arlo')
        self.arlo = Arlo(args.arlo_user, args.arlo_pass)

        self.mc = mqtt.Client()
        self.mc.enable_logger(self.log.getChild('mqtt'))
        self.mc.username_pw_set(args.mqtt_user, args.mqtt_pass)
        if args.tls:
            self.mc.tls_set()

        self.mc.on_connect = self.on_connect
        self.mc.message_callback_add(args.topic_root + '/cmd/+', self.on_base_cmd)
        self.mc.message_callback_add(args.topic_root + '/+/cmd/+', self.on_camera_cmd)

        self.log.info('Connecting to MQTT broker')
        self.mc.connect(args.broker, args.port)
    
    def report_thread_fn(self):
        try:
            while True:
                self.report()
                self.last_reported_ts = time.time()

                if self.stop.wait(self.report_interval):
                    break
        finally:
            self.log.info('Report thread stopped')
            self.stop.set()
    
    def arlo_event_thread_fn(self):
        try:
            self.arlo.HandleEvents(self.arlo_base, self.on_arlo_event)
        finally:
            self.log.info('Arlo event handler stopped')
            self.stop.set()

    def on_arlo_event(self, arlo, event):
        self.log.debug('Received Arlo event %s', json.dumps(event))
    
    def run(self):
        self.arlo_base = self.arlo.GetDevices('basestation')[0]
        self.mc.loop_start()
        self.report_thread.start()

        # Event support isn't robust at the moment. It also interferes with mobile app.
        #self.arlo_event_thread.start()

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
            self.mc.loop_stop()

    def on_connect(self, client, userdata, flags, rc):
        self.log.debug('on_connect. %s', mqtt.connack_string(rc))

        if rc == mqtt.CONNACK_ACCEPTED:
            self.log.info('Connected to MQTT broker. Subscribing to topics')
            self.mc.subscribe(self.topic_root + '/cmd/+')
            self.mc.subscribe(self.topic_root + '/+/cmd/+')
        else:
            self.log.critical('Failed to connect to MQTT broker. %s', mqtt.connack_string(rc))
            self.stop.set()
    
    def on_base_cmd(self, client, userdata, msg):
        parts = msg.topic.split('/')
        cmd = parts[-1]
        payload = str(msg.payload, encoding='utf-8')
        self.log.info('Received base command %s [%s]', cmd, payload)

        if cmd == 'mode':
            self.log.info('Setting Arlo mode to %s', payload)
            self.arlo.CustomMode(self.arlo_base, payload)
            modes = ','.join(self.arlo.GetModesV2()[0]['activeModes'])
            self.publish(self.topic_root + '/activeModes', modes)
        else:
            self.log.warn('Ignoring unknown base command %s', cmd)

    def on_camera_cmd(self, client, userdata, msg):
        parts = msg.topic.split('/')
        cmd = parts[-1]
        camera = parts[-3]
        payload = str(msg.payload, encoding='utf-8')
        self.log.info('Received command %s [%s] for camera %s', cmd, payload, camera)

        if cmd == 'switch':
            privacy = payload.upper() == 'OFF'
            self.log.info('Toggling Arlo camera %s privacy %s', camera, privacy)
            resp = self.arlo.ToggleCamera(self.arlo_base, {'deviceId': camera}, privacy)
            privacy = resp['properties']['privacyActive']
            self.publish('{}/{}/switch'.format(self.topic_root, camera), 'OFF' if privacy else 'ON')
        else:
            self.log.warn('Ignoring unknown camera command %s', cmd)

    def report(self):
        self.log.info('Reporting status')
        states = self.arlo.GetCameraState(self.arlo_base)['properties']

        states = {
            s['serialNumber']: {
                'switch': 'OFF' if s['privacyActive'] else 'ON',
                'batteryLevel': s['batteryLevel'],
                'chargingState': s['chargingState'],
                'connectionState': s['connectionState'],
                'signalStrength': s['signalStrength'],
            }
            for s in states
        }
        states['activeModes'] = ','.join(self.arlo.GetModesV2()[0]['activeModes']) 

        cams = self.arlo.GetDevices('camera')
        for cam in cams:
            device_id = cam['deviceId']
            if device_id in states:
                states[device_id]['lastImageUrl'] = cam['presignedLastImageUrl']

        self.publish(self.topic_root, states)

    def publish(self, topic, value):
        if not isinstance(value, dict):
            self.mc.publish(topic, value)
            return

        for k, v in value.items():
            self.publish('{}/{}'.format(topic, k), v)


def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    parser = argparse.ArgumentParser(description='A simple bridge between Arlo and MQTT.')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debug logging.')
    parser.add_argument('-i', '--report-interval', default=600, type=int,
                        help='Interval in seconds between state refreshes. Defaults to 600.')

    group = parser.add_argument_group('Arlo')
    group.add_argument('--arlo-user', default=os.environ.get('ARLO_USER', None),
                       help='Arlo username. Can also be set via env ARLO_USER.')
    group.add_argument('--arlo-pass', default=os.environ.get('ARLO_PASS', None),
                       help='Arlo password. Can also be set via env ARLO_PASS.')

    group = parser.add_argument_group('MQTT')
    group.add_argument('--broker', default='localhost',
                       help='MQTT broker address. Defaults to localhost.')
    group.add_argument('--port', default=1883, type=int,
                       help='MQTT broker port. Defaults to 1883.')
    group.add_argument('--tls', action='store_true',
                       help='Use TLS connection to MQTT broker.')
    group.add_argument('--mqtt-user', default=os.environ.get('ARLO_MQTT_USER', None),
                       help='MQTT username. Can also be set via env ARLO_MQTT_USER.')
    group.add_argument('--mqtt-pass', default=os.environ.get('ARLO_MQTT_PASS', None),
                       help='MQTT password. Can also be set via env ARLO_MQTT_PASS.')
    group.add_argument('--topic-root', default='arlo',
                       help='MQTT topic root. Defaults to arlo.')

    args = parser.parse_args()
    ArloMqtt(args).run()


if __name__ == "__main__":
    main()
