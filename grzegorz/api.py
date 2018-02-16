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

@bp.get("/playlist")
@response_json
async def get_playlist(request):
    request.app.config["mpv_control"].send_request()
    pass
