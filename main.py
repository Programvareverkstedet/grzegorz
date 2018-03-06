#!/usr/bin/env python3
import os, shutil
import asyncio
import grzegorz

basedir = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(os.path.join(basedir, "config.py")):
	print("copying default_config.py to config.py...")
	shutil.copy(os.path.join(basedir, "default_config.py"), os.path.join(basedir, "config.py"))
import config

async def grzegorz_splash():
    resp = await grzegorz.mpv_control.loadfile('grzegorz/grzegorz/res/logo.jpg')
    #print(resp)

loop, app = grzegorz.make_sanic_app(
    host = config.address,
    port = config.port
)
asyncio.ensure_future(grzegorz_splash())
loop.run_forever()
