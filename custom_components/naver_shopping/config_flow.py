"""Config flow for Hello World integration."""
import logging
import voluptuous as vol
from typing import Any, Dict, Optional
from datetime import datetime

import homeassistant.helpers.config_validation as cv

import homeassistant.helpers.entity_registry

from homeassistant.helpers.device_registry import (
    async_get,
    async_entries_for_config_entry
)

from .const import CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_REFRESH_PERIOD, CONF_KEYWORDS, CONF_SORT_TYPE, CONF_WORD, DOMAIN, CONF_ADD_ANODHER, NAME, REFRESH_MIN, SORT_TYPES, SORT_TYPES_REVERSE

from homeassistant import config_entries, exceptions
from homeassistant.core import callback


_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hello World."""

    VERSION = 1
    # Pick one of the available connection classes in homeassistant/config_entries.py
    # This tells HA if it should be asking for updates, or it'll be notified of updates
    # automatically. This example uses PUSH, as the dummy hub will notify HA of
    # changes.
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL
    data: Optional[Dict[str, Any]]

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Handle the initial step."""
        # This goes through the steps to take the user through the setup process.
        # Using this it is possible to update the UI and prompt for additional
        # information. This example provides a single form (built from `DATA_SCHEMA`),
        # and when that has some validated input, it calls `async_create_entry` to
        # actually create the HA config entry. Note the "title" value is returned by
        # `validate_input` above.
        errors = {}
        if user_input is not None:
            # if user_input[CONF_NETWORK_SEARCH] == True:
            #    return self.async_create_entry(title=user_input[CONF_AREA_NAME], data=user_input)
            # else:
            self.data = user_input
            self.data[CONF_KEYWORDS] = []
            # self.devices = await get_available_device()
            # return await self.async_step_hosts()
            return self.async_create_entry(title=NAME, data=self.data)

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(
                {
                    vol.Required(CONF_CLIENT_ID): cv.string,
                    vol.Required(CONF_CLIENT_SECRET): cv.string
                }), errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Handle a option flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handles options flow for the component."""

    def __init__(self, config_entry) -> None:
        self.config_entry = config_entry
        self.data = {}
        self.data[CONF_KEYWORDS] = config_entry.data[CONF_KEYWORDS]

    async def async_step_init(
        self, user_input: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Manage the options for the custom component."""
        errors: Dict[str, str] = {}
        # Grab all configured repos from the entity registry so we can populate the
        # multi-select dropdown that will allow a user to remove a repo.
        # entity_registry = await async_get_registry(self.hass)

        # entries = async_entries_for_config_entry(
        #    entity_registry, self.config_entry.entry_id
        # )
        # for e in entries:
        #    _LOGGER.debug("entries : " + e.entity_id)
        # Default value for our multi-select.
        #entity_map = {e.entity_id : e for e in entries}
        all_entities = {}
        all_entities_by_id = {}

        entity_registry = homeassistant.helpers.entity_registry.async_get(
            self.hass)
        entities = homeassistant.helpers.entity_registry.async_entries_for_config_entry(
            entity_registry, self.config_entry.entry_id)

        device_registry = async_get(self.hass)
        devices = async_entries_for_config_entry(
            device_registry, self.config_entry.entry_id)

        # for e in entities:
        #    _LOGGER.debug("entity id : %s, name : %s",e.entity_id, e.original_name)

        # Default value for our multi-select.

        for host in self.data[CONF_KEYWORDS]:
            for e in entities:
                if e.original_name == host[CONF_WORD] + "-" + SORT_TYPES_REVERSE[host[CONF_SORT_TYPE]]:
                    name = e.original_name

                    all_entities[e.entity_id] = '{}'.format(
                        name)

                    all_entities_by_id[(
                        host[CONF_WORD],
                        host[CONF_SORT_TYPE],
                        host[CONF_REFRESH_PERIOD]
                    )] = e.entity_id

        if user_input is not None:
            if not errors:
                # If user ticked the box show this form again so they can add an
                # additional repo.
                # remove devices
                self.data[CONF_KEYWORDS].clear()
                remove_entities = []

                for key in all_entities_by_id:
                    if all_entities_by_id[key] not in user_input[CONF_KEYWORDS]:
                        _LOGGER.debug("remove entity : %s",
                                      all_entities_by_id[key])
                        remove_entities.append(all_entities_by_id[key])
                    else:
                        _LOGGER.debug("append entity : %s", key[0])
                        self.data[CONF_KEYWORDS].append(
                            {
                                CONF_WORD: key[0],
                                CONF_SORT_TYPE: key[1],
                                CONF_REFRESH_PERIOD: key[2]
                            }
                        )

                for id in remove_entities:
                    entity_registry.async_remove(id)

                if user_input.get(CONF_ADD_ANODHER, False):
                    return await self.async_step_entity()

                if len(self.data[CONF_KEYWORDS]) <= 0:
                    for d in devices:
                        device_registry.async_remove_device(d.id)

                # User is done adding repos, create the config entry.
                self.data["modifydatetime"] = datetime.now()
                return self.async_create_entry(title=NAME, data=self.data)

        options_schema = vol.Schema(
            {
                vol.Optional(CONF_KEYWORDS, default=list(all_entities)): cv.multi_select(all_entities),
                vol.Optional(CONF_ADD_ANODHER): cv.boolean,
            }
        )

        return self.async_show_form(
            step_id="init", data_schema=options_schema, errors=errors
        )

    async def async_step_entity(self, user_input: Optional[Dict[str, Any]] = None):
        """Second step in config flow to add a repo to watch."""
        errors: Dict[str, str] = {}
        if user_input is not None:

            if not errors:
                # Input is valid, set data.
                self.data[CONF_KEYWORDS].append(
                    {
                        CONF_WORD: user_input.get(CONF_WORD, user_input[CONF_WORD]),
                        CONF_SORT_TYPE: SORT_TYPES[user_input.get(CONF_SORT_TYPE, user_input[CONF_SORT_TYPE])],
                        CONF_REFRESH_PERIOD: user_input.get(
                            CONF_REFRESH_PERIOD, user_input[CONF_REFRESH_PERIOD])
                    }
                )

                # If user ticked the box show this form again so they can add an
                # additional repo.
                if user_input.get(CONF_ADD_ANODHER, False):
                    return await self.async_step_entity()
                # User is done adding repos, create the config entry.
                _LOGGER.debug("call async_create_entry")
                self.data["modifydatetime"] = datetime.now()
                return self.async_create_entry(title=NAME, data=self.data)

        return self.async_show_form(
            step_id="entity",
            data_schema=vol.Schema(
                    {
                        vol.Required(CONF_WORD, default=None): cv.string,
                        vol.Required(CONF_SORT_TYPE, default=SORT_TYPES_REVERSE["sim"]): vol.In([SORT_TYPES_REVERSE["sim"],
                                                                                                 SORT_TYPES_REVERSE["asc"],
                                                                                                 SORT_TYPES_REVERSE["dsc"],
                                                                                                 SORT_TYPES_REVERSE["date"]
                                                                                                 ]),
                        vol.Required(CONF_REFRESH_PERIOD, default=REFRESH_MIN): int,
                        vol.Optional(CONF_ADD_ANODHER): cv.boolean,
                    }
            ), errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""
