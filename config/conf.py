from platform import platform
from typing import Any, Dict

from config.conf_dev import CONF_DEV
from config.conf_prod import CONF_PROD


CONF: Dict[str, Any] = {}


if "Windows" in platform():
    CONF = CONF_DEV
else:
    CONF = CONF_PROD