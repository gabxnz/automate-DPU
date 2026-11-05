import os

DEBUG = os.environ.get("DEBUG", "False").lower() in ["true", "1"]
TIMEOUT = int(os.environ.get("TIMEOUT", 15))

MOODLE_URL = os.environ.get("MOODLE_URL", "https://ead.dpu.def.br")
MOODLE_API_TOKEN = os.environ.get("MOODLE_API_TOKEN", "")
POWER_AUTOMATE_URL = os.environ.get("POWER_AUTOMATE_URL", "")