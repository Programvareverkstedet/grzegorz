from .metadatafetch import get_metadata
from . import nyasync

#Used in api.playlist_get() and api.loadfile()
class PlaylistDataCache:
    def __init__(self, auto_fetch_data = False):
        self.filepath_data_map = {}
        self.auto_fetch_data = auto_fetch_data
        self.jobs = None

    def add_data(self, filepath, data=None):
        if data:
            self.filepath_data_map[filepath] = data

    async def run(self):
        if not self.auto_fetch_data: return

        self.jobs = nyasync.Queue()
        async for filename in self.jobs:
            print("Fetching metadata for ", repr(filename))
            data = await get_metadata(filename)
            #might already be gone by this point:
            if filename in self.filepath_data_map:
                self.filepath_data_map[filename].update(data)
                del self.filepath_data_map[filename]["fetching"]

    def add_data_to_playlist(self, playlist):
        seen = set()

        for item in playlist:
            if "filename" in item:
                seen.add(item["filename"])
                if item["filename"] in self.filepath_data_map:
                    new_item = item.copy()
                    new_item["data"] = self.filepath_data_map[item["filename"]]
                    yield new_item
                    continue
                elif self.auto_fetch_data:
                    self.filepath_data_map[item["filename"]] = {"fetching":True}
                    self.jobs.put_nowait(item["filename"])
                    new_item = item.copy()
                    new_item["data"] = {"fetching":True}
                    yield new_item
                    continue
            yield item

        not_seen = set(self.filepath_data_map.keys()) - seen
        for name in not_seen:
            del self.filepath_data_map[name]
