import asyncio
from sanic import Blueprint, response
from sanic_openapi import doc
from functools import wraps
from . import mpv
from .playlist_data import PlaylistDataCache

bp = Blueprint("grzegorz-api", strict_slashes=True)
# this blueprint assumes a mpv.MPVControl instance is available
# at request.app.config["mpv_control"]

#route decorators:
def response_json(func):
    @wraps(func)
    async def newfunc(*args, **kwargs):
        try: 
            request = args[0]
            mpv_control = request.app.config["mpv_control"]
            out = await func(*args, mpv_control, **kwargs)
            if "error" not in out:
                out["error"] = False
            if "request" in out:
                del out["request"]
            if "mpv_control" in out:
                del out["mpv_control"]
            return response.json(out)
        except Exception as e:
            return response.json({
                "error": e.__class__.__name__,
                "errortext": str(e)
                })
    return newfunc
def response_text(func):
    @wraps(func)
    async def newfunc(*args, **kwargs):
        body = await func(*args, **kwargs)
        return response.text(body)
    return newfunc

class APIError(Exception): pass

PLAYLIST_DATA_CACHE = PlaylistDataCache(auto_fetch_data=True)

#routes:
@bp.get("")
@doc.exclude(True)
@response_text
async def root(request):
    return "Hello friend, I hope you're having a lovely day"

@bp.post("/load")
@doc.summary("Add item to playlist")
@doc.consumes({"path": doc.String("Link to the resource to enqueue")}, required=True)
@doc.consumes({"body":doc.Dictionary(description="Any data you want stored with the queued item")}, location="body")
@response_json
async def loadfile(request, mpv_control):
    if "path" not in request.args:
        raise APIError("No query parameter \"path\" provided")
    if request.json:
        PLAYLIST_DATA_CACHE.add_data(request.args["path"][0], request.json)
    success = await mpv_control.loadfile(request.args["path"][0])
    return locals()

@bp.get("/play")
@doc.summary("Check whether the player is paused or playing")
@response_json
async def play_get(request, mpv_control):
    value = await mpv_control.pause_get() == False
    return locals()

@bp.post("/play")
@doc.summary("Set whether the player is paused or playing")
@doc.consumes({"play": doc.Boolean("Whether to be playing or not")})
@response_json
async def play_set(request, mpv_control):
    if "play" not in request.args:
        raise APIError("No query parameter \"play\" provided")
    success = await mpv_control \
        .pause_set(str(request.args["play"][0]).lower() not in ["true", "1"])
    return locals()

@bp.get("/volume")
@doc.summary("Get the current player volume")
@response_json
async def volume_get(request, mpv_control):
    value = await mpv_control.volume_get()
    return locals()

@bp.post("/volume")
@doc.summary("Set the player volume")
@doc.consumes({"volume": doc.Integer("A number between 0 and 100")})
@response_json
async def volume_set(request, mpv_control):
    if "volume" not in request.args:
        raise APIError("No query parameter \"volume\" provided")
    success = await mpv_control \
        .volume_set(int(request.args["volume"][0]))
    return locals()

@bp.get("/time")
@doc.summary("Get current playback position")
@response_json
async def time_get(request, mpv_control):
    value = {
        "current": await mpv_control.time_pos_get(),
        "left": await mpv_control.time_remaining_get(),
    }
    value["total"] = value["current"] + value["left"]
    return locals()

@bp.post("/time")
@doc.summary("Set playback position")
@doc.consumes({"pos": doc.Float("Seconds to seek to"), "pos": doc.Integer("Percent to seek to")})
@response_json
async def time_set(request, mpv_control):
    if "pos" in request.args:
        success = await mpv_control.seek_absolute(float(request.args["pos"][0]))
    elif "percent" in request.args:
        success = await mpv_control.seek_percent(int(request.args["percent"][0]))
    else:
        raise APIError("No query parameter \"pos\" or \"percent\"provided")
    return locals()

@bp.get("/playlist")
@doc.summary("Get the current playlist")
@response_json
async def playlist_get(request, mpv_control):
    value = await mpv_control.playlist_get()
    value = list(PLAYLIST_DATA_CACHE.add_data_to_playlist(value))
    for i, v in enumerate(value):
        v["index"] = i
        if "current" in v and v["current"] == True:
            v["playing"] = await mpv_control.pause_get() == False
    if value: del i, v
    return locals()

@bp.post("/playlist/next")
@doc.summary("Skip to the next item in the playlist")
@response_json
async def playlist_next(request, mpv_control):
    success = await mpv_control.playlist_next()
    return locals()

@bp.post("/playlist/previous")
@doc.summary("Go back to the previous item in the playlist")
@response_json
async def playlist_previous(request, mpv_control):
    success = await mpv_control.playlist_prev()
    return locals()

@bp.delete("/playlist")
@doc.summary("Clears single item or whole playlist")
@doc.consumes({"index": doc.Integer("Index to item in playlist to remove. If unset, the whole playlist is cleared")})
@response_json
async def playlist_remove_or_clear(request, mpv_control):
    if "index" in request.args:
        success = await mpv_control.playlist_remove(int(request.args["index"][0]))
        action = f"remove #{request.args['index'][0]}"
    else:
        success = await mpv_control.playlist_clear()
        action = "clear all"
    return locals()

@bp.post("/playlist/move")
@doc.summary("Move playlist item to new position")
@doc.description(
    "Move the playlist entry at index1, so that it takes the "
    "place of the entry index2. (Paradoxically, the moved playlist "
    "entry will not have the index value index2 after moving if index1 "
    "was lower than index2, because index2 refers to the target entry, "
    "not the index the entry will have after moving.)")
@doc.consumes({"index2": int}, required=True)
@doc.consumes({"index1": int}, required=True)
@response_json
async def playlist_move(request, mpv_control):
    if "index1" not in request.args or "index2" not in request.args:
        raise APIError(
            "Missing at least one of the required query "
            "parameters: \"index1\" and \"index2\"")
    success = await mpv_control.playlist_move(
        int(request.args["index1"][0]),
        int(request.args["index2"][0]))
    return locals()

@bp.post("/playlist/shuffle")
@doc.summary("Clears single item or whole playlist")
@response_json
async def playlist_shuffle(request, mpv_control):
    success = await mpv_control.playlist_shuffle()
    return locals()
