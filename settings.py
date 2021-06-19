from __future__ import unicode_literals

from django.conf import settings
from django.test.signals import setting_changed

import importlib


# Copied shamelessly from Django REST Framework

DEFAULTS = {
    "RESPONSES": {
        "DEFAULT_RESPONSE_VERB": "detail",
        "LOGGER_OBJ": logging,
        "RAW_TYPES": (int, str, bytes, list, dict),
    },
    "SERVICES": {
        "LOGGER_OBJ": logging,
        "RAISE_EXCEPTION": False,
        "DEFAULT_ERROR_LOG_MESSAGE": "An error happened in your service. That is "
                                     "the default message for the service error",
        "FORCE_ERROR_MESSAGE_ARGUMENT": True,
        "FORCE_INFO_MESSAGE_ARGUMENT": True,
    }
}


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    """ Attempt to import a class from a string representation. """
    try:
        parts = val.split(".")
        module_path, class_name = ".".join(parts[:-1]), parts[-1]
        module = importlib.import_module(module_path)
        return getattr(module, class_name)

    except (ImportError, AttributeError) as exc:
        raise ImportError(
            f"Could not import '{val}' for django-heaven"
            f" setting '{setting_name}'. {exc.__class__.__name__}: {exc}."
        )


class DjangoHeavenSettings:
    def __init__(self, user_settings=None, defaults=None, import_strings=None):
        if user_settings:
            self._user_settings = user_settings
        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "DJANGO_HEAVEN", {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError(f"Invalid django-heaven setting: '{attr}'")

        try:
            val = self.user_settings[attr]
        except KeyError:
            val = self.defaults[attr]

        if attr in self.import_strings:
            val = perform_import(val, attr)

        setattr(self, attr, val)
        return val


graphene_settings = DjangoHeavenSettings(None, DEFAULTS, IMPORT_STRINGS)


def reload_graphene_settings(*args, **kwargs):
    global graphene_settings
    setting, value = kwargs["setting"], kwargs["value"]
    if setting == "DJANGO_HEAVEN":
        graphene_settings = DjangoHeavenSettings(value, DEFAULTS, IMPORT_STRINGS)


setting_changed.connect(reload_graphene_settings)
