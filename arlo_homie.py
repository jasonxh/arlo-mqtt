from homie.device_base import Device_Base
from homie.node.node_base import Node_Base
from homie.node.node_switch import Node_Switch
from homie.node.property.property_battery import Property_Battery
from homie.node.property.property_boolean import Property_Boolean
from homie.node.property.property_integer import Property_Integer
from homie.node.property.property_string import Property_String


class HomieArloCamera(Device_Base):
    def __init__(self, id, name, mqtt_settings, arlo, base_station, log):
        super().__init__(device_id=id, name=name, mqtt_settings=mqtt_settings)

        self.add_node(HomieArloCamera._Node(
            device=self, arlo=arlo, base_station=base_station, log=log))

        self.start()

    @property
    def node(self):
        return self.get_node('camera')

    class _Node(Node_Base):
        def __init__(self, device, arlo, base_station, log):
            super().__init__(device=device, id='camera', name='Camera', type_='camera')

            self.arlo = arlo
            self.base_station = base_station
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
                Property_String(node=self, id='last-image', name='Last Image'))

        def _set_switch(self, value):
            privacy = not value
            self.log.info('Toggling Arlo camera %s privacy %s',
                          self.name, privacy)

            resp = self.arlo.ToggleCamera(
                self.base_station, {'deviceId': self.device.device_id}, privacy)

            self.privacy_active = resp['properties']['privacyActive']

        @property
        def privacy_active(self):
            return not _parse_bool(self.get_property('switch').value)

        @privacy_active.setter
        def privacy_active(self, value):
            value = not value
            self.log.debug('[%s] Updating switch to %s',
                           self.device.name, value)
            self.get_property('switch').value = str(value).lower()

        @property
        def battery_level(self):
            return self.get_property('battery').value

        @battery_level.setter
        def battery_level(self, value):
            self.log.debug('[%s] Updating battery to %d',
                           self.device.name, value)
            self.get_property('battery').value = value

        @property
        def charging_state(self):
            return self.get_property('charging').value

        @charging_state.setter
        def charging_state(self, value):
            self.log.debug('[%s] Updating charging to %s',
                           self.device.name, value)
            self.get_property('charging').value = value

        @property
        def connection_state(self):
            return self.get_property('connection').value

        @connection_state.setter
        def connection_state(self, value):
            self.log.debug('[%s] Updating connection to %s',
                           self.device.name, value)
            self.get_property('connection').value = value

        @property
        def signal_strength(self):
            return self.get_property('signal').value

        @signal_strength.setter
        def signal_strength(self, value):
            self.log.debug('[%s] Updating signal to %d',
                           self.device.name, value)
            self.get_property('signal').value = value

        @property
        def last_image(self):
            return self.get_property('last-image').value

        @last_image.setter
        def last_image(self, value):
            self.log.debug('[%s] Updating last-image to %s',
                           self.device.name, value)
            self.get_property('last-image').value = value


class HomieArloBaseStation(Device_Base):
    def __init__(self, id, name, mqtt_settings, arlo, base_station, log):
        super().__init__(device_id=id, name=name, mqtt_settings=mqtt_settings)

        self.add_node(HomieArloBaseStation._Node(
            device=self, arlo=arlo, base_station=base_station, log=log))

        self.start()

    @property
    def node(self):
        return self.get_node('base-station')

    class _Node(Node_Base):
        def __init__(self, device, arlo, base_station, log):
            super().__init__(device=device, id='base-station',
                             name='Base Station', type_='base-station')

            self.arlo = arlo
            self.base_station = base_station
            self.log = log

            self.add_property(
                Property_String(node=self, id='active-modes', name='Active Modes',
                                settable=True, set_value=self._set_active_modes))

        def _set_active_modes(self, value):
            self.log.info('Setting Arlo mode to %s', value)
            self.arlo.CustomMode(self.base_station, value)

        @property
        def active_modes(self):
            return self.get_property('active-modes').value

        @active_modes.setter
        def active_modes(self, value):
            self.log.debug('[%s] Updating active-modes to %s',
                           self.device.name, value)
            self.get_property('active-modes').value = value


def _parse_bool(value):
    if isinstance(value, bool):
        return value

    s = str(value).lower()
    return s == 'true' or s == '1'
