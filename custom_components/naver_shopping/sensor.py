"""Platform for sensor integration."""
# This file shows the setup for the sensors associated with the cover.
# They are setup in the same way with the call to the async_setup_entry function
# via HA from the module __init__. Each sensor has a device_class, this tells HA how
# to display it in the UI (for know types). The unit_of_measurement property tells HA
# what the unit is, so it can display the correct range. For predefined types (such as
# battery), the unit_of_measurement should match what's expected.
import logging
from threading import Timer
import aiohttp

import json
import asyncio

from .const import *
from homeassistant.helpers.entity import async_generate_entity_id
from homeassistant.components.sensor import SensorEntity


_LOGGER = logging.getLogger(__name__)

# See cover.py for more details.
# Note how both entities for each roller sensor (battry and illuminance) are added at
# the same time to the same list. This way only a single async_add_devices call is
# required.

ENTITY_ID_FORMAT = DOMAIN + ".{}"

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""

    hass.data[DOMAIN]["listener"] = []

    device = Device(NAME)
    client_id = config_entry.data.get(CONF_CLIENT_ID)
    client_secret = config_entry.data.get(CONF_CLIENT_SECRET)

    new_devices = []

    for entity in config_entry.options.get(CONF_KEYWORDS, {}):
        new_devices.append(
            NaverShoppingSensor(
                hass,
                device,
                client_id,
                client_secret,
                entity.get(CONF_WORD),
                entity.get(CONF_SORT_TYPE),
                entity.get(CONF_FILTER, []),
                entity.get(CONF_EXCLUDE, []),
                entity.get(CONF_REFRESH_PERIOD)
            )
        )

    if new_devices:
        async_add_devices(new_devices)


class Device:
    """Dummy roller (device for HA) for Hello World example."""

    def __init__(self, name):
        """Init dummy roller."""
        self._id = name
        self.name = name
        self._callbacks = set()
        self._loop = asyncio.get_event_loop()
        # Reports if the roller is moving up or down.
        # >0 is up, <0 is down. This very much just for demonstration.

        # Some static information about this device
        self.firmware_version = VERSION
        self.model = NAME
        self.manufacturer = NAME

    @property
    def device_id(self):
        """Return ID for roller."""
        return self._id

    def register_callback(self, callback):
        """Register callback, called when Roller changes state."""
        self._callbacks.add(callback)

    def remove_callback(self, callback):
        """Remove previously registered callback."""
        self._callbacks.discard(callback)

    # In a real implementation, this library would call it's call backs when it was
    # notified of any state changeds for the relevant device.
    async def publish_updates(self):
        """Schedule call all registered callbacks."""
        for callback in self._callbacks:
            callback()

    def publish_updates(self):
        """Schedule call all registered callbacks."""
        for callback in self._callbacks:
            callback()

# This base class shows the common properties and methods for a sensor as used in this
# example. See each sensor for further details about properties and methods that
# have been overridden.


class SensorBase(SensorEntity):
    """Base representation of a Hello World Sensor."""

    should_poll = False

    def __init__(self, device):
        """Initialize the sensor."""
        self._device = device

    # To link this entity to the cover device, this property must return an
    # identifiers value matching that used in the cover, but no other information such
    # as name. If name is returned, this entity will then also become a device in the
    # HA UI.
    @property
    def device_info(self):
        """Information about this entity/device."""
        return {
            "identifiers": {(DOMAIN, self._device.device_id)},
            # If desired, the name for the device could be different to the entity
            "name": self._device.device_id,
            "sw_version": self._device.firmware_version,
            "model": self._device.model,
            "manufacturer": self._device.manufacturer
        }

    # This property is important to let HA know if this entity is online or not.
    # If an entity is offline (return False), the UI will refelect this.
    @property
    def available(self) -> bool:
        """Return True if roller and hub is available."""
        return True

    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        # Sensors should also register callbacks to HA when their state changes
        self._device.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Entity being removed from hass."""
        # The opposite of async_added_to_hass. Remove any registered call backs here.
        self._device.remove_callback(self.async_write_ha_state)


class NaverShoppingSensor(SensorBase):
    """Representation of a Thermal Comfort Sensor."""
    _attr_has_entity_name = True
    
    def __init__(self, hass, device, client_id, client_secret, word, sort_type, filter, exclude, refresh_period):
        """Initialize the sensor."""
        super().__init__(device)

        self.hass = hass
        self._word = word

        self.entity_id = async_generate_entity_id(
            ENTITY_ID_FORMAT, "{}_{}_{}".format(NAME, word, sort_type), hass=hass)
        self._name = "{}-{}".format(word, SORT_TYPES_REVERSE[sort_type])
        self._unit_of_measurement = "KRW"
        self._state = None
        self._extra_state_attributes = {}
        self._extra_state_attributes[CONF_SORT_TYPE] = SORT_TYPES_REVERSE[sort_type]
        self._extra_state_attributes[CONF_FILTER] = filter
        self._extra_state_attributes[CONF_EXCLUDE] = exclude
        self._icon = None
        self._value = None
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_period = refresh_period
        self._sort_type = sort_type

        self._filter = ""
        self._exclude = ""
        for f in self._filter:
            self._filter = self._filter + f

        for e in self._exclude:
            self._exclude = self._exclude + e + ":"

        self._filter = filter
        self._exclude = exclude

        # self._device_class = SENSOR_TYPES[sensor_type][0]
        self._unique_id = self.entity_id
        self._device = device
        self._loop = asyncio.get_event_loop()
        Timer(1, self.refreshTimer).start()
    
    def refreshTimer(self):
        self._loop.create_task(self.get_price())
        Timer(self._refresh_period*60, self.refreshTimer).start()

    async def get_price(self):
        try:
            headers: dict = {
                "X-Naver-Client-Id": self._client_id,
                "X-Naver-Client-Secret": self._client_secret,
            }
            
            async with aiohttp.ClientSession(headers = headers) as session:
                _LOGGER.debug("url : " + CONF_URL)
                
                params = {
                    'query': self._word,
                    'display': DISPLAY_COUNT,
                    'start': DISPLAY_START,
                    'sort': self._sort_type,
                    'filter': self._filter,
                    'exclude': self._exclude
                }
                
                self._value = None
                #_LOGGER.debug("headers : " + session.headers)
                async with session.get(CONF_URL, params=params, headers=headers) as response:
                    #_LOGGER.debug(await response.text())
                    raw_data = await response.read()
                    if response.status == 200:
                        data = json.loads(raw_data)
                        #_LOGGER.debug("json data" + data)
                        self._value = data["items"][0][ATTR_LPRICE]
                        self._extra_state_attributes[ATTR_LINK] = data["items"][0][ATTR_LINK]
                        self._extra_state_attributes[ATTR_TITLE] = data["items"][0][ATTR_TITLE]
                        self._extra_state_attributes[ATTR_HPRICE] = data["items"][0][ATTR_HPRICE]
                        self._extra_state_attributes[ATTR_LPRICE] = data["items"][0][ATTR_LPRICE]
                        self._extra_state_attributes[ATTR_IMAGE] = data["items"][0][ATTR_IMAGE]
                        self._extra_state_attributes[ATTR_BRAND] = data["items"][0][ATTR_BRAND]
                        self._extra_state_attributes[ATTR_MAKER] = data["items"][0][ATTR_MAKER]
                        self._extra_state_attributes[ATTR_MALLNAME] = data["items"][0][ATTR_MALLNAME]
                        self._extra_state_attributes[ATTR_CATEGORY1] = data["items"][0][ATTR_CATEGORY1]
                        self._extra_state_attributes[ATTR_CATEGORY2] = data["items"][0][ATTR_CATEGORY2]
                        self._extra_state_attributes[ATTR_CATEGORY3] = data["items"][0][ATTR_CATEGORY3]
                        self._extra_state_attributes[ATTR_CATEGORY4] = data["items"][0][ATTR_CATEGORY4]
                        self._device.publish_updates()
        except:
            _LOGGER.error("get price error")
        
        finally:
            _LOGGER.debug("call next timer")
            #Timer(self._refresh_period*60, self._loop.create_task(self.get_price())).start()

            
    """Sensor Properties"""
    @property
    def entity_picture(self):
        try:
            return self._extra_state_attributes[ATTR_IMAGE]
        except:
            return None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._extra_state_attributes

    @property
    def unit_of_measurement(self):
        """Return the unit_of_measurement of the device."""
        return self._unit_of_measurement

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._value
    
    @property
    def icon(self):
        return "mdi:currency-krw"
  
    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        if self._unique_id is not None:
            return self._unique_id

    def update(self):
        """Update the state."""
