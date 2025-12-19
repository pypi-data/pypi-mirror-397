"""App settings."""

from django.conf import settings

from cmShoppingList import __version__ as CM_VERSION
HEADER_MESSAGE = getattr(settings, "SHOPPING_LIST_HEADER_MESSAGE", "OMG daddy, please take me shopping at JITA!")