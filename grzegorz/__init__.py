from sanic import Sanic
from pathlib import Path
import traceback
from . import mpv
from . import api

__all__ = ["app"]

module_name = __name__.split(".", 1)[0]
app = Sanic(module_name, env_prefix=module_name.upper() + '_')


# api
app.blueprint(api.bp, url_prefix="/api")
app.add_task(api.PLAYLIST_DATA_CACHE.run())

# openapi:
app.ext.openapi.describe("Grzegorz API",
    version     = "1.0.0.",
    description = "The Grzegorz Brzeczyszczykiewicz API, used to control a running mpv instance",
)


# mpv:
async def runMPVControl():
    app.config["mpv_control"] = mpv.MPVControl()
    try:
        await app.config["mpv_control"].run()
    except:
        traceback.print_exc()
    finally:
        pass #app.stop()

app.add_task(runMPVControl())

# populate playlist
async def ensure_splash():
    here = Path(__file__).parent.resolve()
    while not "mpv_control" in app.config:
        await None
    mpv_control: mpv.MPVControl = app.config["mpv_control"]
    playlist = await mpv_control.playlist_get()
    if len(playlist) == 0:
        print("Adding splash to playlist...")
        await mpv_control.loadfile(here / "res/logo.jpg")

app.add_task(ensure_splash())
