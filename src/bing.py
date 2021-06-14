import json
from datetime import datetime
from pathlib import Path

import requests

BING_URL = "https://www.bing.com"
BING_DAILY_IMAGE = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=de-de"
BING_CACHE = "data/cache"


def get_bing_daily_pic() -> dict:
    """ Retrieve metadata for Image of the Day. """
    today = datetime.today().strftime("%Y-%m-%d")
    cached_file = Path(__file__).parent.parent.joinpath(
        "data", "cache", f"{today}.json")
    
    if cached_file.exists():
        with open(cached_file, "r", encoding="utf-8") as fhandle:
            return json.load(fhandle)

    response = requests.get(BING_DAILY_IMAGE)
    response.raise_for_status()
    image_metadata = response.json()["images"][0]
    
    with open(cached_file, "w", encoding="utf-8") as fhandle:
        json.dump(image_metadata, fhandle)
        
    return image_metadata


def get_image_url() -> str:
    metadata = get_bing_daily_pic()
    return BING_URL + metadata["url"]


def get_image_title() -> str:
    metadata = get_bing_daily_pic()
    return metadata["title"]


def get_image_date() -> str:
    metadata = get_bing_daily_pic()
    date = datetime.strptime(metadata["enddate"], "%Y%m%d").date().isoformat()
    return date


def get_image_country() -> str:
    metadata = get_bing_daily_pic()
    copyright_parts = metadata["copyright"].split(",")

    country = ""
    if len(copyright_parts) == 2:
        country = copyright_parts[-1]
    elif len(copyright_parts) > 2:
        country = copyright_parts[-2]

    if country.find("(") != -1:
        country = country[:country.find("(")].strip()

    return country


def get_image_author() -> str:
    """ Return image author from copyright metadata. """
    metadata = get_bing_daily_pic()
    author = ""
    copyright = metadata["copyright"]

    if copyright.find("©") != -1:
        author = copyright[copyright.find("©") + 1:-1].strip()

    return author


def score_guess(country: str) -> float:
    """ Calculate distance from guess to image location. """
    ...
    return 0.0
