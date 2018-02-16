import asyncio
from sanic import Sanic

from . import mpv
from . import nyasync
from . import api

#global variable:
mpv_control = None#mpv.MPVControl()

async def test():
    await mpv_control.loadfile('grzegorz/res/logo.jpg')

def main(host="0.0.0.0", port=8080, tasks:list = None):
    app = Sanic(__name__)
    app.blueprint(api.bp, url_prefix="/api")
    
    #used to ensure sanic/uvloop creates its asyncio loop before MPVControl tries to use one itself
    async def runMPVControl():
        global mpv_control
        
        mpv_control = mpv.MPVControl()
        app.config["mpv_control"] = mpv_control
        try:
            await mpv_control.run()
        except Exception as e:
            print(e)
        
        print("mpv is no longer running. Stopping Sanic...")
        app.stop()

    if not tasks: tasks = []
    tasks.insert(0, runMPVControl())
    
    for task in tasks:
        app.add_task(task)#instead of ensure_future
    
    app.run(host=host, port=port)
    
if __name__ == '__main__':
    main(tasks=[test()])
