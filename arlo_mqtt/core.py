import logging
import threading
import typing as t
from functools import partial

from pyaarlo import ArloBase, ArloCamera, PyArlo, constant

from arlo_mqtt.homie import HomieArloBaseStation, HomieArloCamera


class ArloMqtt:
    log: logging.Logger
    stop: threading.Event

    arlo_user: str
    arlo_pass: str
    mqtt_settings: t.Dict[str, t.Any]

    arlo: PyArlo
    arlo_bases: t.Dict[str, t.Tuple[ArloBase, HomieArloBaseStation]]
    arlo_cams: t.Dict[str, t.Tuple[ArloCamera, HomieArloCamera]]

    def __init__(
            self,
            arlo_user: str,
            arlo_pass: str,
            mqtt_broker: str,
            mqtt_port: int,
            mqtt_user: str,
            mqtt_pass: str,
            debug: bool = False,
            pyaarlo_extras: t.Dict[str, t.Any] = {},
    ) -> None:
        self.log = logging.getLogger(type(self).__name__)
        if debug:
            self.log.setLevel(logging.DEBUG)

        self.stop = threading.Event()

        self.arlo_user = arlo_user
        self.arlo_pass = arlo_pass
        self.pyaarlo_extras = pyaarlo_extras

        self.mqtt_settings = {
            'MQTT_BROKER': mqtt_broker,
            'MQTT_PORT': mqtt_port,
            'MQTT_USERNAME': mqtt_user,
            'MQTT_PASSWORD': mqtt_pass,
        }

    def run(self) -> None:
        self.log.info('Connecting to Arlo')
        self.arlo = PyArlo(**{
            'username': self.arlo_user,
            'password': self.arlo_pass,
            'save_state': False,
            'stream_timeout': 90,
            **self.pyaarlo_extras,  # Can be used to override anything above
        })

        self.arlo_bases = {
            base.device_id: (base, HomieArloBaseStation(
                id=base.device_id,
                name=base.name,
                mqtt_settings=self.mqtt_settings,
                set_mode=partial(self._set_base_mode, base),
                log=self.log.getChild('homie'),
            ))
            for base in self.arlo.base_stations
        }

        self.arlo_cams = {
            cam.device_id: (cam, HomieArloCamera(
                id=cam.device_id,
                name=cam.name,
                mqtt_settings=self.mqtt_settings,
                set_switch=partial(self._set_camera_switch, cam),
                log=self.log.getChild('homie'),
            ))
            for cam in self.arlo.cameras
        }

        for base, homie in self.arlo_bases.values():
            self._link_base_state(base, homie)

        for cam, homie in self.arlo_cams.values():
            self._link_camera_state(cam, homie)

        # There's no code path that sets this currently.
        self.stop.wait()
        self.log.error('Main thread stopped')

    def _set_base_mode(self, base: ArloBase, mode: str) -> None:
        self.log.info('Setting Arlo mode to %s', mode)
        base.mode = mode

    def _set_camera_switch(self, cam: ArloCamera, on: bool) -> None:
        self.log.info('Turning %s Arlo camera %s',
                      'on' if on else 'off', cam.name)
        if on:
            cam.turn_on()
        else:
            cam.turn_off()

    def _link_base_state(self, base: ArloBase, homie: HomieArloBaseStation) -> None:
        def sync_mode() -> None:
            homie.node.mode = base.mode.lower()

        def sync_available_modes() -> None:
            homie.node.available_modes = base.available_modes

        links: t.Dict[str, t.Callable[[], None]] = {
            constant.MODE_KEY: sync_mode,
            '__NON_EXISTENT_KEY_1': sync_available_modes,
        }

        def cb(device: ArloBase, attr: str, value: t.Any) -> None:
            self.log.debug('[base] device=%s, attr=%s value=%s',
                           device.name, attr, '<bytes>' if isinstance(value, bytes) else value)

            link = links.get(attr)
            if link:
                link()

        base.add_attr_callback('*', cb)

        # Perform initial sync
        for link in links.values():
            link()

    def _link_camera_state(self, cam: ArloCamera, homie: HomieArloCamera) -> None:
        def sync_is_on() -> None:
            homie.node.is_on = cam.is_on

        def sync_battery() -> None:
            homie.node.battery_level = cam.battery_level

        def sync_charging() -> None:
            homie.node.charging_state = cam.is_charging

        def sync_connection() -> None:
            homie.node.connection_state = \
                cam.attribute(constant.CONNECTION_KEY)

        def sync_signal() -> None:
            homie.node.signal_strength = cam.signal_strength

        def sync_last_image() -> None:
            homie.node.last_image = cam.last_image

        def sync_motion() -> None:
            homie.node.motion_detected = cam.attribute(
                constant.MOTION_DETECTED_KEY)

        links: t.Dict[str, t.Callable[[], None]] = {
            constant.PRIVACY_KEY: sync_is_on,
            constant.BATTERY_KEY: sync_battery,
            constant.CHARGING_KEY: sync_charging,
            constant.CONNECTION_KEY: sync_connection,
            constant.SIGNAL_STR_KEY: sync_signal,
            constant.LAST_IMAGE_KEY: sync_last_image,
            constant.LAST_IMAGE_DATA_KEY: sync_last_image,
            constant.MOTION_DETECTED_KEY: sync_motion,
        }

        def cb(device: ArloCamera, attr: str, value: t.Any) -> None:
            self.log.debug('[camera] device=%s, attr=%s value=%s',
                           device.name, attr, '<bytes>' if isinstance(value, bytes) else value)

            link = links.get(attr)
            if link:
                link()

        cam.add_attr_callback('*', cb)

        # Perform initial sync
        for link in links.values():
            link()
