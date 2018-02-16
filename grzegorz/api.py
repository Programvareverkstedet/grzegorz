from sanic import Blueprint, response
import asyncio
from . import mpv

bp = Blueprint("grzegorz-api")
#this blueprint assumes a mpv.MPVControl instance is available at request.app.config["mpv_control"]

#route decorators:
def response_json(func):
    async def newfunc(*args, **kwargs):
        body = await func(*args, **kwargs)
        return response.json(body)
    return newfunc
def response_text(func):
    async def newfunc(*args, **kwargs):
        body = await func(*args, **kwargs)
        return response.text(body)
    return newfunc

#routes:
@bp.get("/")
@response_text
async def root(request):
    return "Hello World!"

#@bp.get("/something")
@response_json
async def noe(request):
    return request.app.config["mpv_control"].loadfile(file)

#@bp.get("/something")
@response_json
async def noe(request):
    return request.app.config["mpv_control"].pause_get()

#@bp.get("/something")
@response_json
async def noe(request):
    return request.app.config["mpv_control"].pause_set(state)

#@bp.get("/something")
@response_json
async def noe(request):
    return request.app.config["mpv_control"].volume_get()

#@bp.get("/something")
@response_json
async def noe(request):
    return request.app.config["mpv_control"].volume_set(volume)

#@bp.get("/something")
@response_json
async def noe(request):
    return request.app.config["mpv_control"].time_pos_get()

#@bp.get("/something")
@response_json
async def noe(request):
    return request.app.config["mpv_control"].time_remaining_get()

#@bp.get("/something")
@response_json
async def noe(request):
    return request.app.config["mpv_control"].seek_relative(seconds)

#@bp.get("/something")
@response_json
async def noe(request):
    return request.app.config["mpv_control"].seek_percent(percent)

#@bp.get("/something")
@response_json
async def noe(request):
    return request.app.config["mpv_control"].playlist_get()

#@bp.get("/something")
@response_json
async def noe(request):
    return request.app.config["mpv_control"].playlist_next()

#@bp.get("/something")
@response_json
async def noe(request):
    return request.app.config["mpv_control"].playlist_prev()

#@bp.get("/something")
@response_json
async def noe(request):
    return request.app.config["mpv_control"].playlist_clear()

#@bp.get("/something")
@response_json
async def noe(request):
    return request.app.config["mpv_control"].playlist_remove(index=None)

#@bp.get("/something")
@response_json
async def noe(request):
    return request.app.config["mpv_control"].playlist_move(index1, index2)

#@bp.get("/something")
@response_json
async def noe(request):
    return request.app.config["mpv_control"].playlist_shuffle()
