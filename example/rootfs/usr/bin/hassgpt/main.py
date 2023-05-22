from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from requests import get, post
import logging
import pprint
import json

from models import LightState, Domain, ClimateState, State

# These two lines enable debugging at httplib level (requests->urllib3->http.client)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# The only thing missing will be the response.body which is not logged.
try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

app = FastAPI(
    title="Home Assistant API",
    description="API for getting state Home Assistant entities, and using services to change the state of these entities",
    version="0.0.1",
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["POST", "GET", "PUT"],
            allow_headers=["*"],
            max_age=3600,
        )
    ])

hass_url = 'https://bh66r0mdsvxxolssbsd3ta8g9dla24vs.ui.nabu.casa' + '/api'
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIxYzllMjc1MmI2ZTc0OTQ1YWFlZmE0NzFlZjIzZGU2MSIsImlhdCI6MTY4NDYwODI1MCwiZXhwIjoxOTk5OTY4MjUwfQ.5Qyg3doXbCHA9UGDQg-5yYCi7Yz625kZn_DEvOGqJ4U",
    "content-type": "application/json",
}


@app.get("/states", response_model_exclude_none=True)
async def get_states():
    """
    fetches the states of entities in all domains from home assistant
    """
    response = get(hass_url + '/states', headers=headers)
    if response.ok:
        res = response.json()
        filtered_response = [d for d in res if any(d['entity_id'].startswith(x)
                                                   for x in ['media_player.', 'light.', 'person.', 'lock.', 'climate.',
                                                             'switch.'])]
        return filtered_response
    else:
        return response.content


@app.post("/light/turn_off", response_model_exclude_none=True)
async def light_turn_off(new_state: LightState):
    """
    Tun off lights
    """
    response = post(hass_url + f"/services/light/turn_off",
                    data=new_state.json(exclude_none=True), headers=headers)
    return response.json() if response.ok else response.content


@app.post("/light/turn_on", response_model_exclude_none=True)
async def light_turn_on(new_state: LightState):
    """
    Tun on lights or change a light's color
    """
    response = post(hass_url + f"/services/light/turn_on",
                    data=new_state.json(exclude_none=True), headers=headers)
    return response.json() if response.ok else response.content


@app.post("/climate/set_temperature", response_model_exclude_none=True)
async def climate_set_temperature(new_state: ClimateState):
    """
    Set the temperature on a climate control system
    """
    response = post(hass_url + f"/services/climate/set_temperature",
                    data=new_state.json(exclude_none=True), headers=headers)
    return response.json() if response.ok else response.content


@app.post("/lock/unlock", response_model_exclude_none=True)
async def unlock(new_state: State):
    """
    Unlocks the given lock
    """
    response = post(hass_url + f"/services/lock/unlock",
                    data=new_state.json(exclude_none=True), headers=headers)
    return response.json() if response.ok else response.content


@app.post("/lock/lock", response_model_exclude_none=True)
async def lock(new_state: State):
    """
    Locks the given lock
    """
    response = post(hass_url + f"/services/lock/lock",
                    data=new_state.json(exclude_none=True), headers=headers)
    return response.json() if response.ok else response.content


@app.post("/switch/turn_off", response_model_exclude_none=True)
async def switch_turn_off(new_state: State):
    """
    turn off the given switch
    """
    response = post(hass_url + f"/services/switch/turn_off",
                    data=new_state.json(exclude_none=True), headers=headers)
    return response.json() if response.ok else response.content


@app.post("/switch/turn_on", response_model_exclude_none=True)
async def switch_turn_on(new_state: State):
    """
    turn on the given switch
    """
    response = post(hass_url + f"/services/switch/turn_on",
                    data=new_state.json(exclude_none=True), headers=headers)
    return response.json() if response.ok else response.content


@app.post("/media_player/pause", response_model_exclude_none=True)
async def media_player_pause(new_state: State):
    """
    pause the media that's playing on the given device
    """
    response = post(hass_url + f"/services/media_player/media_pause",
                    data=new_state.json(exclude_none=True), headers=headers)
    return response.json() if response.ok else response.content


@app.post("/media_player/play", response_model_exclude_none=True)
async def media_player_play(new_state: State):
    """
    play or unpause the media that's playing on the given device
    """
    response = post(hass_url + f"/services/media_player/media_play",
                    data=new_state.json(exclude_none=True), headers=headers)
    return response.json() if response.ok else response.content


app.mount("/.well-known", StaticFiles(directory="static/.well-known"), name="static")
app.mount("/", StaticFiles(directory="static"), name="static")
