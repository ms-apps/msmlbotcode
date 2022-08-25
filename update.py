from logging import (
    FileHandler,
    StreamHandler,
    INFO,
    basicConfig,
    error as log_error,
    info as log_info,
)
from os import path as ospath, environ, execl as osexecl
from datetime import datetime
from subprocess import run as srun
from requests import get as rget
from dotenv import load_dotenv
from sys import executable

CYCLE_DYNO = 15 <= datetime.now().day <= 31

if ospath.exists("log.txt"):
    with open("log.txt", "r+") as f:
        f.truncate(0)

basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[FileHandler("log.txt"), StreamHandler()],
    level=INFO,
)

CONFIG_FILE_URL = environ.get("CONFIG_FILE_URL")
HEROKU_APP_NAME = environ.get("APP_NAME")
log_info(f"CONFIG_FILE_URL: {CONFIG_FILE_URL}")
log_info(f"HEROKU_APP_NAME: {HEROKU_APP_NAME}")

try:
    if len(CONFIG_FILE_URL) == 0:
        raise TypeError
    try:
        res = rget(CONFIG_FILE_URL)
        if res.status_code == 200:
            with open("config.env", "wb+") as f:
                f.write(res.content)
        else:
            log_error(
                f"Failed to download config.env {res.status_code}"
            )
    except Exception as e:
        log_error(f"CONFIG_FILE_URL: {e}")
except:
    pass

load_dotenv("config.env", override=True)


# def getConfig(name: str):
#     return environ[name]


# try:
#     DOUBLE_DYNO = getConfig("DOUBLE_DYNO")
#     DOUBLE_DYNO = DOUBLE_DYNO.lower() == "true"
# except:
#     DOUBLE_DYNO = False

# try:
#     HEROKU_API_KEY = getConfig("HEROKU_API_KEY_A")
#     HEROKU_APP_NAME = getConfig("HEROKU_APP_NAME")
#     if len(HEROKU_API_KEY) == 0 or len(HEROKU_APP_NAME) == 0:
#         raise KeyError
#     if DOUBLE_DYNO:
#         if CYCLE_DYNO:
#             HEROKU_API_KEY = getConfig("HEROKU_API_KEY_B")
#             HEROKU_APP_NAME = getConfig("HEROKU_APP_NAME_B")
#         else:
#             HEROKU_API_KEY = getConfig("HEROKU_API_KEY_A")
#             HEROKU_APP_NAME = getConfig("HEROKU_APP_NAME_A")
#         BASE_URL = f"https://{HEROKU_APP_NAME}.herokuapp.com"
#     LOGGER.info("HEROKU_APP_NAME: %s", HEROKU_APP_NAME)
#     LOGGER.info("BASE_URL: %s", BASE_URL)
# except KeyError:
#     LOGGER.warning("Heroku details not entered.")
#     HEROKU_API_KEY = None
#     HEROKU_APP_NAME = None
#     BASE_URL = None

UPSTREAM_REPO = environ.get("UPSTREAM_REPO")
UPSTREAM_BRANCH = environ.get("UPSTREAM_BRANCH")
try:
    if len(UPSTREAM_REPO) == 0:
        raise TypeError
except:
    UPSTREAM_REPO = "https://github.com/ms-apps/msmlbotcode"
try:
    if len(UPSTREAM_BRANCH) == 0:
        raise TypeError
except:
    UPSTREAM_BRANCH = "main"

if ospath.exists(".git"):
    srun(["rm", "-rf", ".git"])

update = srun(
    [
        f"git init -q \
                 && git config --global user.email msmirror@gmail.com \
                 && git config --global user.name msmlbot \
                 && git add . \
                 && git commit -sm update -q \
                 && git remote add origin {UPSTREAM_REPO} \
                 && git fetch origin -q \
                 && git reset --hard origin/{UPSTREAM_BRANCH} -q"
    ],
    shell=True,
)

if update.returncode == 0:
    log_info(
        "Successfully updated with latest commit from UPSTREAM_REPO"
    )
else:
    log_error(
        "Something went wrong while updating, check UPSTREAM_REPO if valid or not!"
    )
