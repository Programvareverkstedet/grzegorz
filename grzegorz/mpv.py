import os
import asyncio
import json

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
            '--input-ipc-server', self._ipc_endpoint,
            '--idle',
            '--force-window',
            '--fullscreen',
            '--no-terminal',
            '--keep-open', # Keep last frame of video on end of video
            '--no-input-default-bindings',
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
            pass

    async def send_request(self, msg):
        with await self.request_lock:
            # Note: If asyncio.Lock is FIFO, the put can be moved out of the
            # critical section. If await is FIFO, the lock is unnessesary. This
            # is the safest option.
            self.mpv.requests.put_nowait(msg)
            return await self.mpv.responses.get()
    
    #Shorthand command requests:
    async def loadfile(self, file):#appends to playlist and start playback if paused
        return await self.send_request({"command":["loadfile", file, "append-play"]})
    async def pause_get(self):
        return await self.send_request({"command":["get_property", "pause"]})
    async def pause_set(self, state):
        return await self.send_request({"command":["set_property", "pause", bool(state)]})
    async def volume_get(self):
        return await self.send_request({"command":["get_property", "volume"]})
    async def volume_set(self, volume):
        return await self.send_request({"command":["set_property", "volume", volume]})
    async def time_pos_get(self):
        return await self.send_request({"command":["get_property", "time-pos"]})
    async def time_remaining_get(self):
        return await self.send_request({"command":["get_property", "time-remaining"]})
    async def seek_relative(self, seconds):
        return await self.send_request({"command":["seek", seconds, "relative"]})
    async def seek_percent(self, percent):
        return await self.send_request({"command":["seek", percent, "absolute-percent"]})
    async def playlist_get(self):
        return await self.send_request({"command":["get_property", "playlist"]})
    async def playlist_next(self):
        return await self.send_request({"command":["playlist-next", "weak"]})
    async def playlist_prev(self):
        return await self.send_request({"command":["playlist-prev", "weak"]})
    async def playlist_clear(self):
        return await self.send_request({"command":["playlist-clear"]})
    async def playlist_remove(self, index=None):
        return await self.send_request({"command":["playlist-remove", "current" if index==None else index]})
    async def playlist_move(self, index1, index2):
        return await self.send_request({"command":["playlist-move", index1, index2]})
    async def playlist_shuffle(self):
        return await self.send_request({"command":["playlist-shuffle"]})
