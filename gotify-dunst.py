# /// script
# dependencies = [
#     "gotify[stream]>=0.6.0",
#     "loguru>=0.7.3",
#     "requests>=2.32.3",
#     "websocket-client>=1.8.0",
# ]
# ///

import asyncio
import configparser
import subprocess
import time
from pathlib import Path

import requests

try:
    from setproctitle import setproctitle

    setproctitle("gotify-dunst")
except ImportError:
    pass

from gotify import AsyncGotify
from loguru import logger

# Setup and Configuration
config_dir = Path.home() / ".config/gotify-dunst"
config_dir.mkdir(parents=True, exist_ok=True)
config_path = config_dir / "gotify-dunst.conf"
default_config_path = Path("gotify-dunst.conf")

if not config_path.exists():
    logger.info("Configuration file not found. Creating a new one.")
    config_path.write_bytes(default_config_path.read_bytes())

logger.debug(f"Using configuration file: {config_path}")

config = configparser.ConfigParser()
config.read(config_path)

domain = config.get("server", "domain", fallback="push.example.com")
token = config.get("server", "token")
ssl = config.getboolean("server", "ssl", fallback=False)

if domain in ["push.example.com", None]:
    print(
        "Configuration error. Make sure you have properly modified the configuration."
    )
    exit()

cache_dir = Path.home() / ".cache/gotify-dunst"
cache_dir.mkdir(exist_ok=True)


def get_picture(appid):
    """
    Get the picture of an application with the given appid.

    Args:
        appid (int): The id of the application.

    Returns:
        str: The path to the downloaded image file.
    """
    if not isinstance(appid, int):
        raise ValueError("appid must be an integer")

    img_path = cache_dir / f"{appid}.jpg"
    if img_path.exists():
        return str(img_path)

    protocol = "https" if ssl else "http"
    req = requests.Request(f"{protocol}://{domain}/application?token={token}")
    req.headers["User-Agent"] = "Mozilla/5.0"

    try:
        response = requests.get(req)
        response.raise_for_status()
        response_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error occurred during HTTP request: {e}")
        return str(img_path)

    for app in response_data:
        if app["id"] == appid:
            img_url = f"{protocol}://{domain}/{app['image']}?token={token}"
            img_req = requests.Request(img_url)
            img_req.headers["User-Agent"] = "Mozilla/5.0"

            try:
                img_response = requests.get(img_req)
                img_response.raise_for_status()
                img_path.write_bytes(img_response.content)
            except requests.exceptions.RequestException as e:
                print(f"Error occurred during image download: {e}")
            break

    return str(img_path)


def send_notification(m: dict):
    priority_map = {range(1, 4): "low", range(4, 8): "normal", range(8, 11): "critical"}
    priority = next(
        (p for p_range, p in priority_map.items() if m["priority"] in p_range), "normal"
    )

    subprocess.run(
        [
            "notify-send",
            m["title"],
            m["message"],
            "-u",
            priority,
            "-i",
            get_picture(m["appid"]),
            "-a",
            "Gotify",
            "-h",
            "string:desktop-entry:gotify-dunst",
        ],
        check=False,
    )


async def get_messages():
    async_gotify = AsyncGotify(
        base_url=f"{'https' if ssl else 'http'}://{domain}",
        client_token=token,
    )

    async for msg in async_gotify.stream():
        send_notification(msg)


if __name__ == "__main__":
    while True:
        try:
            asyncio.run(get_messages())
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(5)
