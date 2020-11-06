import textwrap
from datetime import datetime, timedelta
from io import BytesIO
from math import ceil
from os import path

from flask import Flask, send_file, Response
from PIL import Image, ImageFont, ImageDraw
# PyCharm will complain about this not resolving, IGNORE IT, IT WORKS
from Api import get_weather, get_quote, LOCATION_NAME

app = Flask(__name__)


DISPLAY_SIZE = (800, 480)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

EXTRA_LARGE_FONT_SIZE = 100
LARGE_FONT_SIZE = 50
MEDIUM_FONT_SIZE = 25
SMALL_FONT_SIZE = 15
EXTRA_SMALL_FONT_SIZE = 10

dir_path = path.dirname(path.realpath(__file__))

OPEN_SANS_EXTRA_LARGE = ImageFont.truetype(path.join(dir_path, "./fonts/OpenSans-Regular.ttf"), EXTRA_LARGE_FONT_SIZE)
OPEN_SANS_LARGE = ImageFont.truetype(path.join(dir_path, "./fonts/OpenSans-Regular.ttf"), LARGE_FONT_SIZE)
OPEN_SANS_MEDIUM = ImageFont.truetype(path.join(dir_path, "./fonts/OpenSans-Regular.ttf"), MEDIUM_FONT_SIZE)
OPEN_SANS_SMALL = ImageFont.truetype(path.join(dir_path, "./fonts/OpenSans-Regular.ttf"), SMALL_FONT_SIZE)
OPEN_SANS_EXTRA_SMALL = ImageFont.truetype(path.join(dir_path, "./fonts/OpenSans-Regular.ttf"), EXTRA_SMALL_FONT_SIZE)
ICON_EXTRA_LARGE = ImageFont.truetype(path.join(dir_path, "./fonts/weathericons-regular-webfont.ttf"), EXTRA_LARGE_FONT_SIZE)
ICON_LARGE = ImageFont.truetype(path.join(dir_path, "./fonts/weathericons-regular-webfont.ttf"), LARGE_FONT_SIZE)
ICON_MEDIUM = ImageFont.truetype(path.join(dir_path, "./fonts/weathericons-regular-webfont.ttf"), MEDIUM_FONT_SIZE)
ICON_SMALL = ImageFont.truetype(path.join(dir_path, "./fonts/weathericons-regular-webfont.ttf"), SMALL_FONT_SIZE)
ICON_EXTRA_SMALL = ImageFont.truetype(path.join(dir_path, "./fonts/weathericons-regular-webfont.ttf"), EXTRA_SMALL_FONT_SIZE)

ICON_MAP = {
    '01d': '\uf00d',
    '02d': '\uf002',
    '03d': '\uf002',
    '04d': '\uf002',
    '09d': '\uf008',
    '10d': '\uf008',
    '11d': '\uf010',
    '13d': '\uf00a',
    '50d': '\uf003',
    '01n': '\uf02e',
    '02n': '\uf086',
    '03n': '\uf086',
    '04n': '\uf086',
    '09n': '\uf036',
    '10n': '\uf036',
    '11n': '\uf02d',
    '13n': '\uf02a',
    '50n': '\uf04a'
}


def create_image() -> Image:
    return Image.new("RGB", DISPLAY_SIZE, WHITE)


def draw_text(img: Image, text: str, position: (int, int), font: ImageFont = OPEN_SANS_MEDIUM, fill: (int, int, int) = BLACK, bounds: (int, int) = DISPLAY_SIZE) -> Image:
    d = ImageDraw.Draw(img)

    (x, y) = position
    # Right align
    if position[0] < 0:
        x, _ = d.textsize(text, font)
        x = bounds[0] - x + position[0]

    # Bottom align
    if position[1] < 0:
        _, y = d.textsize(text, font)
        y = bounds[1] - y + position[1]

    d.multiline_text((x, y), text, fill, font)
    return img


def draw_text_centered(img: Image, text: str, x_bounds: (int, int), y: int, font: ImageFont = OPEN_SANS_MEDIUM, fill: (int, int, int) = BLACK) -> Image:
    d = ImageDraw.Draw(img)
    width, _ = d.textsize(text, font)
    x = (x_bounds[1] - x_bounds[0]) / 2 - (width / 2) + x_bounds[0]
    d.multiline_text((x, y), text, fill, font)
    return img


def draw_text_box(img: Image, text: str, x_bounds: (int, int), y: int, font: ImageFont = OPEN_SANS_MEDIUM, fill: (int, int, int) = BLACK) -> Image:
    bounds = x_bounds[1] - x_bounds[0]
    d = ImageDraw.Draw(img)
    em, _ = d.textsize('M', font)
    lines = '\n'.join(textwrap.wrap(text, width=ceil(bounds / em * 2)))
    d.multiline_text((x_bounds[0], y), lines, fill, font)
    return img


def draw_rect(img: Image, top_left: (int, int), bottom_right: (int, int), fill: (int, int, int) = BLACK) -> Image:
    d = ImageDraw.Draw(img)
    d.rectangle([top_left, bottom_right], fill)
    return img


def draw_line(img: Image, pos1: (int, int), pos2: (int, int), width: int = 2, fill: (int, int, int) = BLACK) -> Image:
    d = ImageDraw.Draw(img)
    d.line((pos1, pos2), fill, width)
    return img


def format_day_time(dt: datetime, offset: int) -> str:
    return (dt + timedelta(seconds=offset)).strftime("%a, %d %h %H:%M")


def format_weekday(dt: datetime, offset: int) -> str:
    return (dt + timedelta(seconds=offset)).strftime("%A")


def format_day(dt: datetime, offset: int) -> str:
    return (dt + timedelta(seconds=offset)).strftime("%d %h")


def format_time(dt: datetime, offset: int) -> str:
    return (dt + timedelta(seconds=offset)).strftime("%H:%M")


def get_now_dt(offset: int) -> str:
    return format_day_time(datetime.utcnow(), offset)


def bearing_to_direction(bearing: int) -> str:
    bearing = bearing % 360

    compass_sector = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW", "N"]

    return compass_sector[int(bearing / 22.5)]


def make_weather_image() -> Image:
    weather = get_weather()
    (quote_text, quote_author) = get_quote()

    current_icon = ICON_MAP[weather['current']['weather'][0]['icon']]
    current_temp = str(int(weather['current']['temp'])) + "°C"

    today_min_temp = str(int(weather['daily'][0]['temp']['min'])) + "°C"
    today_max_temp = str(int(weather['daily'][0]['temp']['max'])) + "°C"
    today_min_max_temp = today_min_temp + " / " + today_max_temp
    today_sunrise = format_time(datetime.fromtimestamp(weather['daily'][0]['sunrise']), weather['timezone_offset'])
    today_sunset = format_time(datetime.fromtimestamp(weather['daily'][0]['sunset']), weather['timezone_offset'])
    today_daytime = today_sunrise + " - " + today_sunset
    today_pressure = str(weather['daily'][0]['pressure']) + "hPa"
    today_humidity = str(weather['daily'][0]['humidity']) + "%"
    today_uv = str(weather['daily'][0]['uvi'])
    today_wind = str(int(weather['current']['wind_speed'])) + "m/s " + bearing_to_direction(weather['current']['wind_deg'])

    # IMAGE CREATION
    img = create_image()

    # HEADER
    header_rect_size = (DISPLAY_SIZE[0], 80)
    draw_rect(img, (0, 0), header_rect_size)
    draw_text(img, LOCATION_NAME, (10, -10), OPEN_SANS_LARGE, WHITE, header_rect_size)  # location name
    draw_text(img, get_now_dt(weather['timezone_offset']), (-10, -10), OPEN_SANS_MEDIUM, WHITE, header_rect_size)  # date & time

    # CURRENT WEATHER
    draw_text(img, "daytime", (-5, 110), OPEN_SANS_SMALL, bounds=(DISPLAY_SIZE[0] / 6 - 25, DISPLAY_SIZE[1]))  # sunrise/sunset caption
    draw_text(img, "pressure", (-5, 145), OPEN_SANS_SMALL, bounds=(DISPLAY_SIZE[0] / 6 - 25, DISPLAY_SIZE[1]))  # pressure caption
    draw_text(img, "humidity", (-5, 180), OPEN_SANS_SMALL, bounds=(DISPLAY_SIZE[0] / 6 - 25, DISPLAY_SIZE[1]))  # humidity caption
    draw_text(img, "Midday UV", (-5, 215), OPEN_SANS_SMALL, bounds=(DISPLAY_SIZE[0] / 6 - 25, DISPLAY_SIZE[1]))  # UV caption
    draw_text(img, "wind", (-5, 250), OPEN_SANS_SMALL, bounds=(DISPLAY_SIZE[0] / 6 - 25, DISPLAY_SIZE[1]))  # wind caption

    draw_text(img, today_daytime, (DISPLAY_SIZE[0] / 6 - 25, 100), OPEN_SANS_MEDIUM)  # sunrise text
    draw_text(img, today_pressure, (DISPLAY_SIZE[0] / 6 - 25, 135), OPEN_SANS_MEDIUM)  # pressure text
    draw_text(img, today_humidity, (DISPLAY_SIZE[0] / 6 - 25, 170), OPEN_SANS_MEDIUM)  # humidity text
    draw_text(img, today_uv, (DISPLAY_SIZE[0] / 6 - 25, 205), OPEN_SANS_MEDIUM)  # UV text
    draw_text(img, today_wind, (DISPLAY_SIZE[0] / 6 - 25, 240), OPEN_SANS_MEDIUM)  # wind text

    draw_line(img, (DISPLAY_SIZE[0] / 3, 90), (DISPLAY_SIZE[0] / 3, 280))  # separator line

    draw_text_centered(img, current_icon, (DISPLAY_SIZE[0] / 3, DISPLAY_SIZE[0] / 3 * 2), 90, ICON_EXTRA_LARGE)  # current weather icon
    draw_text_centered(img, current_temp, (DISPLAY_SIZE[0] / 3, DISPLAY_SIZE[0] / 3 * 2),  200, OPEN_SANS_LARGE)  # current weather temp
    draw_text_centered(img, today_min_max_temp, (DISPLAY_SIZE[0] / 3, DISPLAY_SIZE[0] / 3 * 2), 260, OPEN_SANS_MEDIUM)  # today's min/max

    draw_line(img, (DISPLAY_SIZE[0] / 3 * 2, 90), (DISPLAY_SIZE[0] / 3 * 2, 280))  # separator line

    # QUOTE
    draw_text_box(img, quote_text, (DISPLAY_SIZE[0] / 3 * 2 + 25, DISPLAY_SIZE[0] - 25), 100, OPEN_SANS_SMALL)
    draw_text(img, '- ' + quote_author, (-25, 245), OPEN_SANS_SMALL, bounds=(DISPLAY_SIZE[0], DISPLAY_SIZE[1]))
    draw_text(img, 'theysaidso.com', (-25, 265), OPEN_SANS_EXTRA_SMALL, bounds=(DISPLAY_SIZE[0], DISPLAY_SIZE[1]))

    # FORECAST WEATHER
    for i in range(1, 6):
        forecast = weather['daily'][i]

        x1 = (i - 1) * (DISPLAY_SIZE[0] / 6) + (DISPLAY_SIZE[0] / 12)
        x2 = i * (DISPLAY_SIZE[0] / 6) + (DISPLAY_SIZE[0] / 12)

        icon = ICON_MAP[forecast['weather'][0]['icon']]
        day = format_day(datetime.fromtimestamp(forecast['dt']), weather['timezone_offset'])
        weekday = format_weekday(datetime.fromtimestamp(forecast['dt']), weather['timezone_offset'])
        min_temp = str(int(forecast['temp']['min'])) + "°C"
        max_temp = str(int(forecast['temp']['max'])) + "°C"
        min_max_temp = min_temp + " / " + max_temp

        draw_text_centered(img, icon, (x1, x2), 310, ICON_LARGE)  # forecast icon
        draw_text_centered(img, day, (x1, x2), 380, OPEN_SANS_SMALL)  # forecast date
        draw_text_centered(img, weekday, (x1, x2), 400, OPEN_SANS_SMALL)  # forecast weekday
        draw_text_centered(img, min_max_temp, (x1, x2), 420, OPEN_SANS_SMALL)  # min/max

    return img


def make_error_image(error: Exception) -> Image:
    import traceback
    img = create_image()
    draw_rect(img, (0, 0), (DISPLAY_SIZE[0], 80))
    draw_text(img, "Error!", (10, -10), OPEN_SANS_LARGE, WHITE, (DISPLAY_SIZE[0], 80))

    draw_text(img, str(error), (10, 90), OPEN_SANS_SMALL)
    draw_text(img, traceback.format_exc(), (10, 110), OPEN_SANS_SMALL)
    return img


def serve_image(img: Image):
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


@app.route('/')
def get_image_route():
    return serve_image(make_weather_image())


@app.after_request
def add_header(res: Response):
    res.headers["Pragma"] = "no-cache"
    res.headers["Expires"] = "0"
    res.headers['Cache-Control'] = 'no-store'
    return res


@app.errorhandler(Exception)
def exception_handler(error: Exception):
    return serve_image(make_error_image(error))


if __name__ == "__main__":
    app.run(debug=True)
