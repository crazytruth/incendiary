import re
from typing import Optional, Any

from sanic.request import File

from insanic.conf import settings


HIDDEN_KEY_WORDS = [
    "API",
    "TOKEN",
    "KEY",
    "SECRET",
    "PASS",
    "PROFANITIES_LIST",
    "SIGNATURE",
    "SESSION",
    "EMAIL",
    "PHONE",
]

HIDDEN_SETTINGS = re.compile(
    "|".join(HIDDEN_KEY_WORDS + [v.lower() for v in HIDDEN_KEY_WORDS])
)

CLEANSED_SUBSTITUTE: str = "*********"


def tracing_name(name: Optional[str] = None) -> str:
    """
    Returns that tracing node name. Appends the
    environment with the application's service name.
    """
    if name is None:
        name = settings.SERVICE_NAME
    return f"{name}.{settings.ENVIRONMENT.lower()}"


def abbreviate_for_xray(payload: dict) -> dict:
    """
    If the payload includes a file, the file is translated
    to just it's name and size instead of including the
    whole file.
    """
    for k in payload.keys():
        v = payload.get(k)
        if isinstance(v, File):
            v = {"type": v.type, "size": len(v.body)}
        payload[k] = v
    return payload


def cleanse_value(key: str, value: Any):
    """
    Cleanse an individual setting key/value of sensitive content.
    If the value is a dictionary, recursively cleanse the keys in
    that dictionary.
    """
    try:
        if HIDDEN_SETTINGS.search(key):
            cleansed = CLEANSED_SUBSTITUTE
        else:
            if isinstance(value, dict):
                cleansed = dict(
                    (k, cleanse_value(k, v)) for k, v in value.items()
                )
            else:
                cleansed = value
    except TypeError:
        # If the key isn't regex-able, just return as-is.
        cleansed = value

    return cleansed


def get_safe_dict(target: dict) -> dict:
    """
    Returns a dictionary with sensitive settings blurred out.
    """
    return_value = {}
    for k in target:
        return_value[k] = cleanse_value(k, target.get(k))
    return return_value


def get_safe_settings() -> dict:
    """
    Returns a dictionary of the settings module,
    with sensitive settings blurred out.
    """
    return get_safe_dict(
        {k: getattr(settings, k) for k in dir(settings) if k.isupper()}
    )
