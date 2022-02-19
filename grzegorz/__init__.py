from sanic import Sanic
from sanic_openapi import swagger_blueprint#, openapi2_blueprint
from pathlib import Path
from . import mpv
from . import api

__all__ = ["app"]

module_name = __name__.split(".", 1)[0]
app = Sanic(module_name, env_prefix=module_name.upper() + '_')


# api
app.blueprint(api.bp, url_prefix="/api")
app.add_task(api.PLAYLIST_DATA_CACHE.run())


# openapi:
app.config.API_VERSION = '1.0'
app.config.API_TITLE = 'Grzegorz API'
app.config.API_DESCRIPTION \
    = 'The Grzegorz Brzeczyszczykiewicz API, used to control a running mpv instance'
#app.config.API_TERMS_OF_SERVICE = ''# Supposed to be a link
app.config.API_PRODUCES_CONTENT_TYPES = ['application/json']
app.config.API_CONTACT_EMAIL = 'drift@pvv.ntnu.no'
#app.config.API_LICENSE_NAME = 'MIT'
#app.config.API_LICENSE_URL = 'todo'

#app.blueprint(openapi2_blueprint)
app.blueprint(swagger_blueprint)


# mpv:
app.config["mpv_control"] = mpv.MPVControl()
async def runMPVControl():
    try:
        await app.config["mpv_control"].run()
    finally:
        app.stop()

app.add_task(runMPVControl())

# populate playlist
async def ensure_splash():
    here = Path(__file__).parent.resolve()
    mpv_control: mpv.MPVControl = app.config["mpv_control"]
    playlist = await mpv_control.playlist_get()
    if len(playlist) == 0:
        print("Adding splash to playlist...")
        await mpv_control.loadfile(here / "res/logo.jpg")

app.add_task(ensure_splash())
