import asyncio, uvloop
from sanic import Sanic
from sanic_openapi import swagger_blueprint, openapi_blueprint
from signal import signal, SIGINT

from . import mpv
from . import nyasync
from . import api

#global variable:
mpv_control = None#mpv.MPVControl()

def make_sanic_app(host="0.0.0.0", port=8080):
    global mpv_control

    app = Sanic(__name__)
    app.blueprint(api.bp, url_prefix="/api")
    app.blueprint(openapi_blueprint)
    app.blueprint(swagger_blueprint)
    
    asyncio.set_event_loop(uvloop.new_event_loop())
    server_coro = app.create_server(host=host, port=port)
    loop = asyncio.get_event_loop()
    server_task = asyncio.ensure_future(server_coro)
    signal(SIGINT, lambda s, f: loop.stop())
    
    mpv_control = mpv.MPVControl()
    app.config["mpv_control"] = mpv_control
    async def runMPVControl():
        try:
            await mpv_control.run()
        except Exception as e:
            print(e)
        print("mpv is no longer running. Stopping Sanic...")
        app.stop()
    asyncio.ensure_future(runMPVControl())
    
    return loop, app

def main(tasks:list = []):
    loop, app = make_sanic_app()
    for task in tasks:
        asyncio.ensure_future(task)
    loop.run_forever()
    
if __name__ == '__main__':
    main()
