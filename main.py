#!/usr/bin/env python3
import asyncio
import grzegorz

async def grzegorz_splash():
    resp = await grzegorz.mpv_control.loadfile('grzegorz/grzegorz/res/logo.jpg')
    #print(resp)

loop, app = grzegorz.make_sanic_app()
asyncio.ensure_future(grzegorz_splash())
loop.run_forever()
