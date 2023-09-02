import os
import requests
from fastapi.templating import Jinja2Templates

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

app_dir = os.path.dirname(
    os.path.abspath(__file__))

templates_path = os.path.join(app_dir, 'templates')

templates = Jinja2Templates(directory=templates_path)

static_path = os.path.join(app_dir, 'static')
static_name = os.path.basename(app_dir)

subapp = FastAPI()
subapp.mount("/static", StaticFiles(directory=static_path),
             name=static_name)


def get_current_weather():
    response = requests.get(
        'https://api.open-meteo.com/v1/forecast?latitude=56.8498&longitude=53.2045&current_weather=true&windspeed_unit=ms')
    return response.json()['current_weather']


@subapp.get('/')
def main(request: Request):
    current_weather = get_current_weather()
    print(current_weather)
    return templates.TemplateResponse("index.html", {"request": request, "static_name": static_name, "current_weather": current_weather})
