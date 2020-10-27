from os import getenv
import requests

WEATHER_URL = 'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&appid={appid}&units=metric'
LOCATION_URL = 'https://api.mapbox.com/geocoding/v5/mapbox.places/{lon},{lat}.json?access_token={api}&types=place'

OPEN_WEATHER_MAP_API_KEY = getenv("OPEN_WEATHER_MAP_API")
LOCATION_COORDS = getenv("LOCATION_COORDS")
LOCATION_NAME = getenv("LOCATION_NAME")

if not OPEN_WEATHER_MAP_API_KEY:
    raise Exception("OPEN_WEATHER_MAP_API is not set")

if not LOCATION_COORDS:
    raise Exception("LOCATION_COORDS is not set")

if not LOCATION_NAME:
    raise Exception("LOCATION_NAME is not set")


def get_weather():
    coords = LOCATION_COORDS.split(',')
    url = WEATHER_URL.format(lat=coords[0], lon=coords[1], appid=OPEN_WEATHER_MAP_API_KEY)
    print(f'[FETCHING] {url}')
    r = requests.get(url)
    return r.json()


def _get_location_name():
    coords = LOCATION_COORDS.split(',')
    url = LOCATION_URL.format(lat=coords[0], lon=coords[1], api=MAPBOX_API)
    print(f'[FETCHING] {url}')
    r = requests.get(url)
    res = r.json()
    return res['features'][0]['text']

