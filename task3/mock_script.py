import json
import math
import random
import sys
from datetime import datetime, timedelta

from pymongo import MongoClient
from tqdm import trange

MONGODB_URL = "mongodb://localhost:27017"

NUM_DRIVERS = 3_000
NUM_CLIENTS = 10_000

BASIC_DATE = datetime.now()

DRIVER_REVIEW_RATING_MAX = 5

DRIVER_REVIEW_CATEGORIES = [
    "great music",
    "nice communication",
    "knows city",
    "good auto",
    "superior service",
]

with open("resources/driver_review_text.json") as f:
    DRIVER_REVIEW_TEXT = json.load(f)

CLIENT_REVIEW_RATING_MAX = 5

CLIENT_REVIEW_CATEGORIES = [
    "neat",
    "nice communication",
    "quite and polite",
    "interesting person",
]

amc = MongoClient(MONGODB_URL)
LOCATIONS = list(amc.london.postcodes.find({}, ["_id", "lat", "long"]))


def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 7321 # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(
        math.radians(lat1)
    ) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d


def calculate_price(doc):
    start_loc = doc["start_location"]
    end_loc = doc["end_location"]

    origin = start_loc["lat"], start_loc["long"]
    destination = end_loc["lat"], end_loc["long"]
    peak_factor = (
        1.5 if doc["start_date"].hour in {9, 10, 19, 20, 23, 0, 1, 2, 3, 4, 5} else 1
    )

    return 5.5 * distance(origin, destination) * peak_factor


def create_driver_review():
    driver_review = {}
    if random.random() < 0.7:

        driver_review["rating"] = random.randrange(DRIVER_REVIEW_RATING_MAX)

        if random.random() < 0.3:
            num_cat = random.randint(1, len(DRIVER_REVIEW_CATEGORIES))
            driver_review["categories"] = random.sample(
                DRIVER_REVIEW_CATEGORIES, num_cat
            )

        if random.random() < 0.2:
            driver_review["text"] = random.choice(DRIVER_REVIEW_TEXT)

    return driver_review


def create_client_review():
    client_review = {}

    if random.random() < 0.7:
        client_review["rating"] = random.randrange(CLIENT_REVIEW_RATING_MAX)
        if random.random() < 0.3:
            num_cat = random.randint(1, len(CLIENT_REVIEW_CATEGORIES))
            client_review["categories"] = random.sample(
                CLIENT_REVIEW_CATEGORIES, num_cat
            )
    return client_review


def create_record():
    day = timedelta(days=random.randrange(31))
    duration = timedelta(minutes=random.randint(10, 160))

    doc = {
        "driver_id": random.randrange(NUM_DRIVERS),
        "client_id": random.randrange(NUM_CLIENTS),
        "start_date": BASIC_DATE + day,
        "end_date": BASIC_DATE + day + duration,
        "start_location": random.choice(LOCATIONS),
        "end_location": random.choice(LOCATIONS),
    }

    doc["cost"] = calculate_price(doc)

    if driver_review := create_driver_review():
        doc["driver_review"] = driver_review

    if client_review := create_client_review():
        doc["client_review"] = client_review

    return doc


if __name__ == "__main__":
    num = int(sys.argv[1])
    gen = (create_record() for _ in trange(num))

    amc.admin.command({"shardCollection": "london.taxi_rides", "key": {"_id": "hashed"}})
    amc.london.taxi_rides.insert_many(gen)
