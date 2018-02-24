from sanic import Blueprint, response
import asyncio
from . import mpv

bp = Blueprint("grzegorz-api")
#this blueprint assumes a mpv.MPVControl instance is available at request.app.config["mpv_control"]

#route decorators:
def response_json(func):
    async def newfunc(*args, **kwargs):
        #try: 
            body = await func(*args, **kwargs)
            if "error" not in body:
                body["error"] = False
            if "request" in body:
                del body["request"]
            return response.json(body)
        #except Exception as e:
        #    return response.json({"error": e.__class__.__name__, "error_msg": e.args})
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

@bp.post("/load")
@response_json
async def loadfile(request):
    if "source" not in request.json:
        return {"error", "no param \"source\""}
    success = await request.app.config["mpv_control"].loadfile(request.json["source"])
    return locals()

@bp.get("/play")
@response_json
async def get_play(request):
    value = await request.app.config["mpv_control"].pause_get() == False
    return locals()

@bp.post("/play")
@response_json
async def set_play(request):
    success = await request.app.config["mpv_control"] \
        .pause_set(request.form["play"][0] not in ["true", "1"])
    return locals()

#@bp.get("/something")
@response_json
async def noe(request):
    body = await request.app.config["mpv_control"].volume_get()
    return body

#@bp.get("/something")
@response_json
async def noe(request):
    body = await request.app.config["mpv_control"].volume_set(volume)
    return body

#@bp.get("/something")
@response_json
async def noe(request):
    body = await request.app.config["mpv_control"].time_pos_get()
    return body

#@bp.get("/something")
@response_json
async def noe(request):
    body = await request.app.config["mpv_control"].time_remaining_get()
    return body

#@bp.get("/something")
@response_json
async def noe(request):
    body = await request.app.config["mpv_control"].seek_relative(seconds)
    return body

#@bp.get("/something")
@response_json
async def noe(request):
    body = await request.app.config["mpv_control"].seek_percent(percent)
    return body

@bp.get("/playlist")
@response_json
async def noe(request):
    value = await request.app.config["mpv_control"].playlist_get()
    return locals()

@bp.post("/playlist/next")
@response_json
async def noe(request):
    success = await request.app.config["mpv_control"].playlist_next()
    return locals()

@bp.post("/playlist/previous")
@response_json
async def noe(request):
    success = await request.app.config["mpv_control"].playlist_prev()
    return locals()

#@bp.get("/something")
@response_json
async def noe(request):
    body = await request.app.config["mpv_control"].playlist_clear()
    return body

#@bp.get("/something")
@response_json
async def noe(request):
    body = await request.app.config["mpv_control"].playlist_remove(index=None)
    return body

#@bp.get("/something")
@response_json
async def noe(request):
    body = await request.app.config["mpv_control"].playlist_move(index1, index2)
    return body

#@bp.get("/something")
@response_json
async def noe(request):
    body = await request.app.config["mpv_control"].playlist_shuffle()
    return body
