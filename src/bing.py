import json
import os
import random
from datetime import datetime
from pathlib import Path

import requests
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

API_BASE_URL = "https://maps.googleapis.com/maps/api/streetview"
METADATA_URL = API_BASE_URL + "/metadata"
CACHE_DIR = "data/cache"
API_KEY = os.getenv(
    "GOOGLE_STREETVIEW_API_KEY", "AIzaSyDpkeGQzKGmXGGu364kQ6QTwDFuXkT5CTM"
)


def get_random_streetview_pic() -> dict:
    """Get random image metadata from Google Street View Static API."""
    today = datetime.today().strftime("%Y-%m-%d")
    cached_file = Path(__file__).parent.parent.joinpath(
        "data", "metadata", f"{today}.json"
    )
    cached_file.parent.mkdir(exist_ok=True, parents=True)

    if cached_file.exists():
        with open(cached_file, "r", encoding="utf-8") as fhandle:
            return json.load(fhandle)

    while True:
        location = (random.uniform(-90, 90), random.uniform(-180, 180))
        query_params = {
            "location": ",".join(map(str, location)),
            "radius": 50000,
            "size": "1920x1080",
            "key": API_KEY,
        }
        response = requests.get(METADATA_URL, params=query_params)
        image_metadata = response.json()

        if response.status_code == 200 and image_metadata["status"] == "OK":
            with open(cached_file, "w", encoding="utf-8") as fhandle:
                json.dump(image_metadata, fhandle)

            download_streetview_pic(image_metadata["pano_id"])
            return image_metadata


def download_streetview_pic(pano_id: str):
    query_params = {
        "pano": pano_id,
        "size": "1920x1080",
        "heading": 0,
        "key": API_KEY,
    }
    response = requests.get(API_BASE_URL, params=query_params, stream=True)

    if response.status_code == 200:
        image_type = response.headers["Content-Type"].split("/")[1]
        image_file = Path(__file__).parent.parent.joinpath(
            "data", "images", f"{pano_id}.{image_type}"
        )
        image_file.parent.mkdir(exist_ok=True, parents=True)
        with open(image_file, "wb") as fh:
            for chunk in response:
                fh.write(chunk)


def get_image_path(pano_id: str) -> str:
    image_base_dir = Path(__file__).parent.parent.joinpath("data", "images")
    return str(
        next(image_base_dir.glob(f"{pano_id}.*")).relative_to(
            Path(__file__).parent.parent
        )
    )


def get_image_location_name() -> str:
    metadata = get_random_streetview_pic()
    coord = metadata["location"]["lat"], metadata["location"]["lng"]
    geolocator = Nominatim(user_agent="Bing IOTD Challenge")

    location = geolocator.reverse(coord, language="de")

    return location.address


def score_guess(user_country: str) -> float:
    """Calculate distance from guess to image location."""
    metadata = get_random_streetview_pic()
    geolocator = Nominatim(user_agent="Bing IOTD Challenge")
    user_location = geolocator.geocode(user_country)
    bing_location = metadata["location"]["lat"], metadata["location"]["lng"]
    distance = geodesic(
        (user_location.latitude, user_location.longitude),
        (bing_location[0], bing_location[1]),
    ).km
    return round(distance)


if __name__ == "__main__":
    get_random_streetview_pic()
    name = get_image_location_name()
    score = score_guess("Deutschland")
    print(score)
