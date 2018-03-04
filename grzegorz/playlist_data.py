
#Used in api.playlist_get() and api.loadfile()
class PlaylistDataCache:
    def __init__(self):
        self.filepath_data_map = {}
    
    def add_data(self, filepath, data=None):
        if data:
            self.filepath_data_map[filepath] = data
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
            yield item
        
        not_seen = set(self.filepath_data_map.keys()) - seen
        for name in not_seen:
            del self.filepath_data_map[name]
            
        
