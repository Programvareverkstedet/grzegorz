import os
import asyncio
import json
import time
import shlex
import traceback
from typing import List, Optional, Union
from pathlib import Path

from . import nyasync

IS_DEBUG = os.environ.get("GRZEGORZ_IS_DEBUG", "0") != "0"

class MPV:
    # TODO: move this to /tmp or /var/run ?
    # TODO: make it configurable with an env variable?
    _ipc_endpoint = Path(f"mpv_ipc.socket")

    def __init__(self):
        self.requests = nyasync.Queue()
        self.responses = nyasync.Queue()
        self.events = nyasync.Queue()

    @classmethod
    def mpv_command(cls) -> List[str]:
        return [
            'mpv',
            f'--input-ipc-server={str(cls._ipc_endpoint)}',
            '--pipewire-remote=/run/user/1003/pipewire-0', # Cage doesn't set up XDG variables properly?
            '--idle',
            '--force-window',
            *(('--fullscreen',) if not IS_DEBUG else ()),
            '--ytdl-format=bestvideo[height<=?1080]',
            '--no-terminal',
            '--load-unsafe-playlists',
            '--keep-open', # Keep last frame of video on end of video
            #'--no-input-default-bindings',
        ]

    async def run(self, is_restarted=False, **kw):
        if self._ipc_endpoint.is_socket():
            print("Socket found, try connecting instead of starting our own mpv!")
            self.proc = None # we do not own the socket
            await self.connect(**kw)
        else:
            print("Starting mpv...")
            self.proc = await asyncio.create_subprocess_exec(*self.mpv_command())
            await asyncio.gather(
                self.ensure_running(),
                self.connect(**kw),
            )

    async def connect(self, *, timeout=10):
        await asyncio.sleep(0.5)
        t = time.time()
        while self.is_running and time.time() - t < timeout:
            try:
                self.ipc_conn = await nyasync.UnixConnection.from_path(str(self._ipc_endpoint))
                break
            except (FileNotFoundError, ConnectionRefusedError):
                continue
            await asyncio.sleep(0.1)
        else:
            if time.time() - t >= timeout:
                #raise TimeoutError

                # assume the socket is dead, and start our own instance
                print("Socket not responding. Will try deleting it and start mpv ourselves!")
                self._ipc_endpoint.unlink()
                return await self.run()
            else:
                raise Exception("MPV died before socket connected")

        print("Connected to mpv!")
        # TODO: in this state we are unable to detect if the connection is lost

        self._future_connect = asyncio.gather(
            self.process_outgoing(),
            self.process_incomming(),
        )
        await self._future_connect

    def _cleanup_connection(self):
        assert self.proc is not None # we must own the socket
        self._future_connect.cancel() # reduces a lot of errors on exit
        if self._ipc_endpoint.is_socket():
            self._ipc_endpoint.unlink()

    @property
    def is_running(self) -> bool:
        if self.proc is None: # we do not own the socket
            # TODO: can i check the read and writer?
            return self._ipc_endpoint.is_socket()
        else:
            return self.proc.returncode is None

    async def ensure_running(self):
        await self.proc.wait()
        print("MPV suddenly stopped...")
        self._cleanup_connection()
        await self.run()

    async def process_outgoing(self):
        async for request in self.requests:
            try:
                encoded = json.dumps(request).encode('utf-8')
            except Exception as e:
                print("Unencodable request:", request)
                traceback.print_exception(e)
                continue
            self.ipc_conn.write(encoded)
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
        code = await p.wait()

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


# CLI entrypoint
def print_mpv_command():
    print(*map(shlex.quote, MPV.mpv_command()))
