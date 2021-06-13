from datetime import datetime

import requests

BING_URL = "https://www.bing.com"
BING_DAILY_IMAGE = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=de-de"


def get_bing_daily_pic() -> dict:
    response = requests.get(BING_DAILY_IMAGE)
    response.raise_for_status()
    image_metadata = response.json()["images"][0]
    return image_metadata


def get_image_url() -> str:
    metadata = get_bing_daily_pic()
    return BING_URL + metadata["url"]


def get_image_title() -> str:
    metadata = get_bing_daily_pic()
    return metadata["title"]

def get_image_startdate() -> str:
    metadata = get_bing_daily_pic()
    date = datetime.strptime(metadata["startdate"], "%Y%m%d").date().isoformat()
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


def score_guess(country: str) -> float:
    """ Calculate distance from guess to image location. """
    ...
    return 0.0