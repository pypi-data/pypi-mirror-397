from configparser import ConfigParser
from platformdirs import user_config_dir
from pathlib import Path

_CONFIG: ConfigParser | None = None

def get_config() -> ConfigParser:
    global _CONFIG

    if _CONFIG is None:
        cfgfile = Path(user_config_dir("GregPilotTUI")) / "config.ini"
        config = ConfigParser()
        config.read(cfgfile)
        _CONFIG = config

    return _CONFIG


def reload_config() -> None:
    global _CONFIG
    _CONFIG = None