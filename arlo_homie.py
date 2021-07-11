import typing as t
from logging import Logger

from arlo import Arlo
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
        arlo: Arlo,
        base_station: dict,
        log: Logger,
    ) -> None:
        super().__init__(device_id=id.lower(), name=name, mqtt_settings=mqtt_settings)

        self.arlo_device_id = id
        self.arlo = arlo
        self.base_station = base_station
        self.log = log

        self.add_node(HomieArloCamera._Node(device=self, log=log))

        self.start()

    @property
    def node(self) -> '_Node':
        return self.get_node('camera')

    class _Node(Node_Base):
        def __init__(self, device: 'HomieArloCamera', log: Logger) -> None:
            super().__init__(device=device, id='camera', name='Camera', type_='camera')

            self.log = log

            self.add_property(
                Property_Boolean(node=self, id='switch', name='Switch', set_value=self._set_switch))
            self.add_property(
                Property_Battery(node=self))
            self.add_property(
                Property_String(node=self, id='charging', name='Charging'))
            self.add_property(
                Property_String(node=self, id='connection', name='Connection'))
            self.add_property(
                Property_Integer(node=self, id='signal', name='Signal', settable=False))
            self.add_property(
                Property_String(node=self, id='lastimage', name='Last Image'))

        def _set_switch(self, on: bool) -> None:
            privacy = not on
            self.log.info('Toggling Arlo camera %s privacy %s',
                          self.name, privacy)

            resp = self.device.arlo.ToggleCamera(
                self.device.base_station, {'deviceId': self.device.arlo_device_id}, privacy)

            self.privacy_active = resp['properties']['privacyActive']

        @property
        def privacy_active(self) -> bool:
            return not _parse_bool(self.get_property('switch').value)

        @privacy_active.setter
        def privacy_active(self, privacy: bool) -> None:
            on = not privacy
            self.log.debug('[%s] Updating switch to %s',
                           self.device.name, on)
            self.get_property('switch').value = str(on).lower()

        @property
        def battery_level(self) -> int:
            return self.get_property('battery').value

        @battery_level.setter
        def battery_level(self, value: int) -> None:
            self.log.debug('[%s] Updating battery to %d',
                           self.device.name, value)
            self.get_property('battery').value = value

        @property
        def charging_state(self) -> str:
            return self.get_property('charging').value

        @charging_state.setter
        def charging_state(self, value: str) -> None:
            self.log.debug('[%s] Updating charging to %s',
                           self.device.name, value)
            self.get_property('charging').value = value

        @property
        def connection_state(self) -> str:
            return self.get_property('connection').value

        @connection_state.setter
        def connection_state(self, value: str) -> None:
            self.log.debug('[%s] Updating connection to %s',
                           self.device.name, value)
            self.get_property('connection').value = value

        @property
        def signal_strength(self) -> int:
            return self.get_property('signal').value

        @signal_strength.setter
        def signal_strength(self, value: int) -> None:
            self.log.debug('[%s] Updating signal to %d',
                           self.device.name, value)
            self.get_property('signal').value = value

        @property
        def last_image(self) -> str:
            return self.get_property('lastimage').value

        @last_image.setter
        def last_image(self, value: str) -> None:
            self.log.debug('[%s] Updating lastimage to %s',
                           self.device.name, value)
            self.get_property('lastimage').value = value


class HomieArloBaseStation(Device_Base):
    def __init__(
        self,
        id: str,
        name: str,
        mqtt_settings: t.Dict[str, t.Any],
        arlo: Arlo,
        base_station: dict,
        log: Logger,
    ) -> None:
        super().__init__(device_id=id.lower(), name=name, mqtt_settings=mqtt_settings)

        self.arlo_device_id = id
        self.arlo = arlo
        self.base_station = base_station
        self.log = log

        self.add_node(HomieArloBaseStation._Node(device=self, log=log))

        self.start()

    @property
    def node(self) -> '_Node':
        return self.get_node('basestation')

    class _Node(Node_Base):
        def __init__(self, device: 'HomieArloBaseStation', log: Logger) -> None:
            super().__init__(device=device, id='basestation',
                             name='Base Station', type_='basestation')

            self.log = log

            self.add_property(
                Property_String(node=self, id='activemodes', name='Active Modes',
                                settable=True, set_value=self._set_active_modes))

        def _set_active_modes(self, value: str) -> None:
            self.log.info('Setting Arlo mode to %s', value)
            self.device.arlo.CustomMode(self.device.base_station, value)

        @property
        def active_modes(self) -> str:
            return self.get_property('activemodes').value

        @active_modes.setter
        def active_modes(self, value: str) -> None:
            self.log.debug('[%s] Updating activemodes to %s',
                           self.device.name, value)
            self.get_property('activemodes').value = value


def _parse_bool(value) -> bool:
    if isinstance(value, bool):
        return value

    s = str(value).lower()
    return s == 'true' or s == '1'
