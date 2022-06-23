"""Constants for the Detailed Hello World Push integration."""
from typing import DefaultDict
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

# This is the internal name of the integration, it should also match the directory
# name for the integration.
DOMAIN = "naver_shopping"
NAME = "Naver Shopping"
VERSION = "1.0.1"

CONF_ADD_ANODHER = "add_another"

CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_id2"
CONF_SEARCH_KEYWORD = "search_keyword"
CONF_KEYWORDS = "keywords"
CONF_WORD = "word"
CONF_REFRESH_PERIOD = "refresh_period"

CONF_URL = "https://openapi.naver.com/v1/search/shop.json"


DISPLAY_COUNT = 1
DISPLAY_START = 1
SORT_TYPE = "sim"
REFRESH_MIN = 60

ATTR_LINK = "link"
ATTR_TITLE = "title"
ATTR_HPRICE = "hprice"
ATTR_LPRICE = "lprice"
ATTR_IMAGE = "image"
ATTR_BRAND = "brand"
ATTR_MAKER = "maker"
ATTR_MALLNAME = "mallName"
ATTR_CATEGORY1 = "category1"
ATTR_CATEGORY2 = "category2"
ATTR_CATEGORY3 = "category3"
ATTR_CATEGORY4 = "category4"

OPTIONS = [
    (CONF_WORD, "", cv.string),
    (CONF_REFRESH_PERIOD, REFRESH_MIN, vol.All(vol.Coerce(float), vol.Range(0, 1))),
]
