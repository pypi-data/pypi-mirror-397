from pathlib import Path

LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

ORG = "baylorgenetics"
API_VERSION = "7.0"

DEFAULT_ENV_FILE = Path("~/.config/jps-ado-pr-utils/.env").expanduser()
