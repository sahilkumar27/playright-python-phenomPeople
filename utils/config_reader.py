import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# USERNAME = (
#     os.getenv("BASE_URL")
#     or os.getenv("BASE_URL")
#     or os.getenv("standard_user")
#     or "standard_user"
# )
# PASSWORD = (
#     os.getenv("SAUCE_PASSWORD")
#     or os.getenv("SAUCEDEMO_PASSWORD")
#     or os.getenv("secret_sauce")
#     or "secret_sauce"
# )
#



# Project root directory
ROOT_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(ROOT_DIR / ".env")


class ConfigReader:

    BASE_URL = os.getenv("BASE_URL")

    BROWSER = os.getenv("BROWSER", "chromium")

    HEADLESS = os.getenv(
        "HEADLESS", "false"
    ).lower() == "true"

    SLOW_MO = int(os.getenv("SLOW_MO", "300"))

    DEFAULT_TIMEOUT = int(
        os.getenv("DEFAULT_TIMEOUT", "15000")
    )

    USERNAME = os.getenv("PHENOM_USERNAME")

    PASSWORD = os.getenv("PHENOM_PASSWORD")