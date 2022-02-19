import os
import asyncio
import json
from shlex import quote
from typing import List, Optional, Union

from . import nyasync


class MPV:
    _ipc_endpoint = 'mpv_ipc.socket'

    def __init__(self):
        self.requests = nyasync.Queue()
        self.responses = nyasync.Queue()
        self.events = nyasync.Queue()

    async def run(self):
        self.proc = await asyncio.create_subprocess_exec(
            'mpv',
            '--input-ipc-server=' + quote(self._ipc_endpoint),
            '--idle',
            '--force-window',
            '--fullscreen',
            '--no-terminal',
            '--load-unsafe-playlists',
            '--keep-open', # Keep last frame of video on end of video
            #'--no-input-default-bindings',
            )

        while self.is_running():
            try:
                self.ipc_conn = await nyasync.unix_connection(self._ipc_endpoint)
                break
            except (FileNotFoundError, ConnectionRefusedError):
                continue
            await asyncio.sleep(0.1)
        else:
            raise Exception("MPV died before socket connected")
        
        self._future = asyncio.gather(
            self.ensure_running(),
            self.process_outgoing(),
            self.process_incomming(),
        )
        await self._future

    def _cleanup(self):
        if os.path.exists(self._ipc_endpoint):
            os.remove(self._ipc_endpoint)
        self._future.cancel()#reduces a lot of errors on exit

    def is_running(self):
        return self.proc.returncode is None

    async def ensure_running(self):
        await self.proc.wait()
        self._cleanup()
        raise Exception("MPV died unexpectedly")

    async def process_outgoing(self):
        async for request in self.requests:
            self.ipc_conn.write(json.dumps(request).encode('utf-8'))
            self.ipc_conn.write(b'\n')

    async def process_incomming(self):
        async for response in self.ipc_conn:
            msg = json.loads(response)
            if 'event' in msg:
                self.events.put_nowait(msg)
            else: # response
                self.responses.put_nowait(msg)

class MPVError(Exception):
    pass

class MPVControl:
    def __init__(self):
        self.mpv = MPV()
        self.request_lock = asyncio.Lock()

    async def run(self):
        await asyncio.gather(
            self.mpv.run(),
            self.process_events(),
        )

    async def process_events(self):
        async for event in self.mpv.events:
            # TODO: print?
            pass

    async def send_request(self, msg):
        async with self.request_lock:
            # Note: If asyncio.Lock is FIFO, the put can be moved out of the
            # critical section. If await is FIFO, the lock is unnessesary. This
            # is the safest option.
            self.mpv.requests.put_nowait(msg)
            return await self.mpv.responses.get()

    #other commands:
    async def wake_screen(self):
        # TODO: use this
        # TODO: wayland counterpart
        p = await asyncio.create_subprocess_exec(
            "xset",
            "-display",
            os.environ["DISPLAY"],
            "dpms",
            "force",
            "on"
            )
        code = await process.wait()

    #Shorthand command requests:

    async def loadfile(self, file: Union[str, Path]):
        "appends to playlist and start playback if paused"

        if isinstance(file, Path):
            file = str(file)
        resp = await self.send_request({"command":["loadfile", file, "append-play"]})
        return resp["error"] == "success"

    async def pause_get(self):
        resp = await self.send_request({"command":["get_property", "pause"]})
        if "error" in resp and resp["error"] != "success":
            raise MPVError("Unable to get whether paused or not: " + resp["error"])
        return resp["data"] if "data" in resp else None

    async def pause_set(self, state: bool):
        resp = await self.send_request({"command":["set_property", "pause", bool(state)]})
        return resp["error"] == "success"

    async def volume_get(self):
        resp = await self.send_request({"command":["get_property", "volume"]})
        if "error" in resp and resp["error"] != "success":
            raise MPVError("Unable to get volume! " + resp["error"])
        return resp["data"] if "data" in resp else None

    async def volume_set(self, volume: int):
        resp = await self.send_request({"command":["set_property", "volume", volume]})
        return resp["error"] == "success"

    async def time_pos_get(self):
        resp = await self.send_request({"command":["get_property", "time-pos"]})
        if "error" in resp and resp["error"] != "success":
            raise MPVError("Unable to get time pos: " + resp["error"])
        return resp["data"] if "data" in resp else None

    async def time_remaining_get(self):
        resp = await self.send_request({"command":["get_property", "time-remaining"]})
        if "error" in resp and resp["error"] != "success":
            raise MPVError("Unable to get time left:" + resp["error"])
        return resp["data"] if "data" in resp else None

    async def seek_absolute(self, seconds: float):
        resp = await self.send_request({"command":["seek", seconds, "absolute"]})
        return resp["data"] if "data" in resp else None

    async def seek_relative(self, seconds: float):
        resp = await self.send_request({"command":["seek", seconds, "relative"]})
        return resp["data"] if "data" in resp else None

    async def seek_percent(self, percent: float):
        resp = await self.send_request({"command":["seek", percent, "absolute-percent"]})
        return resp["data"] if "data" in resp else None

    async def playlist_get(self):
        resp = await self.send_request({"command":["get_property", "playlist"]})
        if "error" in resp and resp["error"] != "success":
            raise MPVError("Unable to get playlist:" + resp["error"])
        return resp["data"] if "data" in resp else None

    async def playlist_next(self):
        resp = await self.send_request({"command":["playlist-next", "weak"]})
        return resp["error"] == "success"

    async def playlist_prev(self):
        resp = await self.send_request({"command":["playlist-prev", "weak"]})
        return resp["error"] == "success"

    async def playlist_goto(self, index):
        resp = await self.send_request({"command":["set_property", "playlist-pos", index]})
        return resp["error"] == "success"

    async def playlist_clear(self):
        resp = await self.send_request({"command":["playlist-clear"]})
        return resp["error"] == "success"

    async def playlist_remove(self, index: Optional[int] = None):
        resp = await self.send_request({"command":["playlist-remove", "current" if index==None else index]})
        return resp["error"] == "success"

    async def playlist_move(self, index1: int, index2: int):
        resp = await self.send_request({"command":["playlist-move", index1, index2]})
        return resp["error"] == "success"

    async def playlist_shuffle(self):
        resp = await self.send_request({"command":["playlist-shuffle"]})
        return resp["error"] == "success"

    async def playlist_get_looping(self):
        resp = await self.send_request({"command":["get_property", "loop-playlist"]})
        return resp["data"] == "inf" if "data" in resp else False

    async def playlist_set_looping(self, value: bool):
        resp = await self.send_request({"command":["set_property", "loop-playlist", "inf" if value else "no"]})
        return resp["error"] == "success"
