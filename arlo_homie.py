import json
import typing as t
from enum import Enum, unique
from logging import Logger

from homie.device_base import Device_Base
from homie.node.node_base import Node_Base
from homie.node.property.property_battery import Property_Battery
from homie.node.property.property_boolean import Property_Boolean
from homie.node.property.property_integer import Property_Integer
from homie.node.property.property_string import Property_String


class HomieArloCamera(Device_Base):
    def __init__(
        self,
        id: str,
        name: str,
        mqtt_settings: t.Dict[str, t.Any],
        set_switch: t.Callable[[bool], None],
        log: Logger,
    ) -> None:
        super().__init__(device_id=id.lower(), name=name, mqtt_settings=mqtt_settings)

        self.set_switch = set_switch
        self.log = log

        self.add_node(self.Node(device=self, log=log))

        self.start()

    @property
    def node(self) -> 'Node':
        return self.get_node(self.Node.ID)

    class Node(Node_Base):
        ID: t.ClassVar[str] = 'camera'
        device: 'HomieArloCamera'

        @unique
        class _PropertyId(Enum):
            SWITCH = 'switch'
            BATTERY = 'battery'
            CHARGING = 'charging'
            CONNECTION = 'connection'
            SIGNAL = 'signal'
            LAST_IMAGE = 'lastimage'
            MOTION_DETECTED = 'motiondetected'

        def __init__(self, device: 'HomieArloCamera', log: Logger) -> None:
            super().__init__(device=device, id=self.ID, name='Camera', type_='camera')

            self.log = log

            self.add_property(Property_Boolean(
                node=self,
                id=self._PropertyId.SWITCH.value,
                name='Switch',
                set_value=device.set_switch,
            ))
            self.add_property(Property_Battery(
                node=self,
                id=self._PropertyId.BATTERY.value,
            ))
            self.add_property(Property_String(
                node=self,
                id=self._PropertyId.CHARGING.value,
                name='Charging',
            ))
            self.add_property(Property_String(
                node=self,
                id=self._PropertyId.CONNECTION.value,
                name='Connection',
            ))
            self.add_property(Property_Integer(
                node=self,
                id=self._PropertyId.SIGNAL.value,
                name='Signal',
                settable=False,
            ))
            self.add_property(Property_String(
                node=self,
                id=self._PropertyId.LAST_IMAGE.value,
                name='Last Image',
            ))
            self.add_property(Property_Boolean(
                node=self,
                id=self._PropertyId.MOTION_DETECTED.value,
                name='Motion Detected',
                settable=False,
            ))

        @property
        def is_on(self) -> bool:
            return _parse_bool(self.get_property(self._PropertyId.SWITCH.value).value)

        @is_on.setter
        def is_on(self, on: bool) -> None:
            self.log.debug('[%s] Updating switch to %s',
                           self.device.name, on)
            self.get_property(self._PropertyId.SWITCH.value).value = \
                str(on).lower()

        @property
        def battery_level(self) -> int:
            return self.get_property(self._PropertyId.BATTERY.value).value

        @battery_level.setter
        def battery_level(self, value: int) -> None:
            self.log.debug('[%s] Updating battery to %d',
                           self.device.name, value)
            self.get_property(self._PropertyId.BATTERY.value).value = value

        @property
        def charging_state(self) -> str:
            return self.get_property(self._PropertyId.CHARGING.value).value

        @charging_state.setter
        def charging_state(self, value: t.Union[str, bool]) -> None:
            if isinstance(value, bool):
                value = 'On' if value else 'Off'

            self.log.debug('[%s] Updating charging to %s',
                           self.device.name, value)
            self.get_property(self._PropertyId.CHARGING.value).value = value

        @property
        def connection_state(self) -> str:
            return self.get_property(self._PropertyId.CONNECTION.value).value

        @connection_state.setter
        def connection_state(self, value: str) -> None:
            self.log.debug('[%s] Updating connection to %s',
                           self.device.name, value)
            self.get_property(self._PropertyId.CONNECTION.value).value = value

        @property
        def signal_strength(self) -> int:
            return self.get_property(self._PropertyId.SIGNAL.value).value

        @signal_strength.setter
        def signal_strength(self, value: int) -> None:
            self.log.debug('[%s] Updating signal to %d',
                           self.device.name, value)
            self.get_property(self._PropertyId.SIGNAL.value).value = value

        @property
        def last_image(self) -> str:
            return self.get_property(self._PropertyId.LAST_IMAGE.value).value

        @last_image.setter
        def last_image(self, value: str) -> None:
            self.log.debug('[%s] Updating last image to %s',
                           self.device.name, value)
            self.get_property(self._PropertyId.LAST_IMAGE.value).value = value

        @property
        def motion_detected(self) -> bool:
            return _parse_bool(self.get_property(self._PropertyId.MOTION_DETECTED.value).value)

        @motion_detected.setter
        def motion_detected(self, value: bool) -> None:
            self.log.debug('[%s] Updating motion detected to %s',
                           self.device.name, value)
            self.get_property(self._PropertyId.MOTION_DETECTED.value).value = \
                str(value).lower()


class HomieArloBaseStation(Device_Base):
    def __init__(
        self,
        id: str,
        name: str,
        mqtt_settings: t.Dict[str, t.Any],
        set_mode: t.Callable[[str], None],
        log: Logger,
    ) -> None:
        super().__init__(device_id=id.lower(), name=name, mqtt_settings=mqtt_settings)

        self.set_mode = set_mode
        self.log = log

        self.add_node(self.Node(device=self, log=log))

        self.start()

    @property
    def node(self) -> 'Node':
        return self.get_node(self.Node.ID)

    class Node(Node_Base):
        ID: t.ClassVar[str] = 'basestation'
        device: 'HomieArloBaseStation'

        @unique
        class _PropertyId(Enum):
            MODE = 'mode'
            AVAILABLE_MODES = 'availablemodes'

        def __init__(self, device: 'HomieArloBaseStation', log: Logger) -> None:
            super().__init__(device=device, id=self.ID, name='Base Station', type_='basestation')

            self.log = log

            self.add_property(Property_String(
                node=self,
                id=self._PropertyId.MODE.value,
                name='Mode',
                settable=True,
                set_value=device.set_mode,
            ))

            self.add_property(Property_String(
                node=self,
                id=self._PropertyId.AVAILABLE_MODES.value,
                name='Available Modes',
                settable=False,
            ))

        @property
        def mode(self) -> str:
            return self.get_property(self._PropertyId.MODE.value).value

        @mode.setter
        def mode(self, value: str) -> None:
            self.log.debug('[%s] Updating mode to %s', self.device.name, value)
            self.get_property(self._PropertyId.MODE.value).value = value

        @property
        def available_modes(self) -> t.List[str]:
            return json.loads(self.get_property(self._PropertyId.AVAILABLE_MODES.value).value)

        @available_modes.setter
        def available_modes(self, modes: t.List[str]) -> None:
            value = json.dumps(modes)
            self.log.debug('[%s] Updating available modes to %s',
                           self.device.name, value)
            self.get_property(self._PropertyId.MODE.value).value = value


def _parse_bool(value) -> bool:
    if isinstance(value, bool):
        return value

    s = str(value).lower()
    return s == 'true' or s == '1'
