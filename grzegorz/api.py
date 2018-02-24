from sanic import Blueprint, response
import asyncio
from . import mpv

bp = Blueprint("grzegorz-api")
# this blueprint assumes a mpv.MPVControl instance is available
# at request.app.config["mpv_control"]

#route decorators:
def response_json(func):
    async def newfunc(*args, **kwargs):
        try: 
            mpv_control = args[0].app.config["mpv_control"]
            body = await func(*args, mpv_control, **kwargs)
            if "error" not in body:
                body["error"] = False
            if "request" in body:
                del body["request"]
            if "mpv_control" in body:
                del body["mpv_control"]
            return response.json(body)
        except Exception as e:
            return response.json({
                "error": e.__class__.__name__,
                "errortext": str(e)
                })
    return newfunc
def response_text(func):
    async def newfunc(*args, **kwargs):
        body = await func(*args, **kwargs)
        return response.text(body)
    return newfunc

class APIError(Exception): pass

#routes:
@bp.get("/")
@response_text
async def root(request):
    return "Hello World!"

@bp.post("/load")
@response_json
async def loadfile(request, mpv_control):
    if "path" not in request.form:
        raise APIError("no form argument \"path\" provided")
    success = await mpv_control.loadfile(request.form["path"][0])
    return locals()

@bp.get("/play")
@response_json
async def play_get(request, mpv_control):
    value = await mpv_control.pause_get() == False
    return locals()

@bp.post("/play")
@response_json
async def play_set(request, mpv_control):
    if "play" not in request.form:
        raise APIError("No form argument \"play\" provided")
    success = await mpv_control \
        .pause_set(request.form["play"][0] not in ["true", "1"])
    return locals()

@bp.get("/volume")
@response_json
async def volume_get(request, mpv_control):
    value = await mpv_control.volume_get()
    return locals()

@bp.post("/volume")
@response_json
async def volume_set(request, mpv_control):
    if "volume" not in request.form:
        raise APIError("No form argument \"volume\" provided")
    success = await mpv_control \
        .volume_set(int(request.form["volume"][0]))
    return locals()

#@bp.get("/something")
@response_json
async def noe(request, mpv_control):
    body = await mpv_control.time_pos_get()
    return body

#@bp.get("/something")
@response_json
async def noe(request, mpv_control):
    body = await mpv_control.time_remaining_get()
    return body

#@bp.get("/something")
@response_json
async def noe(request, mpv_control):
    body = await mpv_control.seek_relative(seconds)
    return body

#@bp.get("/something")
@response_json
async def noe(request, mpv_control):
    body = await mpv_control.seek_percent(percent)
    return body

@bp.get("/playlist")
@response_json
async def playlist_get(request, mpv_control):
    value = await mpv_control.playlist_get()
    for i, v in enumerate(value):
        if "current" in v and v["current"] == True:
            v["playing"] = await mpv_control.pause_get() == False
    return locals()

@bp.post("/playlist/next")
@response_json
async def playlist_next(request, mpv_control):
    success = await mpv_control.playlist_next()
    return locals()

@bp.post("/playlist/previous")
@response_json
async def playlist_previous(request, mpv_control):
    success = await mpv_control.playlist_prev()
    return locals()

#@bp.get("/something")
@response_json
async def noe(request, mpv_control):
    body = await mpv_control.playlist_clear()
    return body

#@bp.get("/something")
@response_json
async def noe(request, mpv_control):
    body = await mpv_control.playlist_remove(index=None)
    return body

#@bp.get("/something")
@response_json
async def noe(request, mpv_control):
    body = await mpv_control.playlist_move(index1, index2)
    return body

#@bp.get("/something")
@response_json
async def noe(request, mpv_control):
    body = await mpv_control.playlist_shuffle()
    return body
