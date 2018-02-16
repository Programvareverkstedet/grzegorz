import asyncio

from . import mpv
from . import nyasync

mpv_control = mpv.MPVControl()

async def test():
    await mpv_control.loadfile('grzegorz/res/logo.jpg')

async def entry():
    await asyncio.gather(
        mpv_control.run(),
        test(),
    )

def main():
    nyasync.run(entry())

if __name__ == '__main__':
    main()
