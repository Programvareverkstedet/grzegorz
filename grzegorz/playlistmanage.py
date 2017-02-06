import asyncio

from . import metadatafetch
from . import nyasync

metadatafetch_queue = nyasync.Queue()
async def metadatafetch_loop():
    async for item in metadatafetch_queue:
        title = await metadatafetch.title(item.url)
        item.title = title
        metadatafetch_queue.task_done()

class PlaylistItem:
    def __init__(self, url):
        self.url = url
        self.title = None

class Playlist:
    def __init__(self):
        self.playlist = []
        self.nonempty = nyasync.Condition(lambda: self.playlist)
        self.change = nyasync.Event()

    def queue(self, url):
        item = PlaylistItem(url)
        self.playlist.append(item)
        metadatafetch_queue.put_nowait(item)
        self.nonempty.notify()
        self.change.notify()

    async def dequeue(self):
        await self.nonempty
        self.change.notify()
        return self.playlist.pop(0)
