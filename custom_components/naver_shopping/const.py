"""Constants for the Detailed Hello World Push integration."""
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

# This is the internal name of the integration, it should also match the directory
# name for the integration.
DOMAIN = "naver_shopping"
NAME = "Naver Shopping"
VERSION = "1.0.8"

CONF_OPTION_MODIFY = "option_modify"
CONF_OPTION_ADD = "option_add"
CONF_OPTION_SELECT = "option_select"
CONF_OPTION_DELETE = "option_delete"
CONF_OPTION_ENTITIES = "option_entities"

CONF_OPTIONS = [
    CONF_OPTION_MODIFY,
    CONF_OPTION_ADD
]

CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_id2"
CONF_SEARCH_KEYWORD = "search_keyword"
CONF_KEYWORDS = "keywords"
CONF_WORD = "word"
CONF_REFRESH_PERIOD = "refresh_period"
CONF_SORT_TYPE = "sort_type"

CONF_FILTER = "filter"
CONF_EXCLUDE = "exclude"

FILTER_TYPES = {
    "네이버페이 연동 상품": "naverpay"
}

FILTER_TYPES_REVERSE = {
    "naverpay": "네이버페이 연동 상품"
}

EXCLUDE_TYPES = {
    "중고": "used",
    "렌탈": "rental",
    "해외직구,구매대행": "cbshop"
}

EXCLUDE_TYPES_REVERSE = {
    "used":"중고",
    "rental": "렌탈",
    "cbshop": "해외직구,구매대행"
}

SORT_TYPES = {
    "유사도순": "sim",
    "가격낮은순": "asc",
    "가격높은순": "dsc",
    "등록날짜순": "date"
}

SORT_TYPES_REVERSE = {
    "sim": "유사도순",
    "asc": "가격낮은순",
    "dsc": "가격높은순",
    "date": "등록날짜순"
}

CONF_URL = "https://openapi.naver.com/v1/search/shop.json"


DISPLAY_COUNT = 1
DISPLAY_START = 1
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
