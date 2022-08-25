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
log_info(f"HEROKU_APP_NAME: {HEROKU_APP_NAME}")
log_info(f"CYCLE_DYNO: {CYCLE_DYNO}")

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


def getConfig(name: str):
    i = environ[name]
    log_info(f"{name}: {i}")
    return i


def update_repo():
    try:
        UPSTREAM_REPO = getConfig("UPSTREAM_REPO")
        UPSTREAM_BRANCH = getConfig("UPSTREAM_BRANCH")
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


try:
    DOUBLE_DYNO = getConfig("DOUBLE_DYNO")
    DOUBLE_DYNO = DOUBLE_DYNO.lower() == "true"
except:
    DOUBLE_DYNO = False

try:
    if (
        DOUBLE_DYNO
        & CYCLE_DYNO
        & (HEROKU_APP_NAME != getConfig("HEROKU_APP_NAME_B"))
    ) or (
        DOUBLE_DYNO
        & (not CYCLE_DYNO)
        & (HEROKU_APP_NAME != getConfig("HEROKU_APP_NAME_A"))
    ):
        log_info("Need to change dyno")
    else:
        log_info("Good to Go!")
        log_info(f"Current App Name {HEROKU_APP_NAME}")
        update_repo()
        srun("python3", "-m", "bot", check=True)
except KeyError:
    BASE_URL = None
    log_error("Something went wrong")
