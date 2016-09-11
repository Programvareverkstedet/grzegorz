from lib.python_mpv.mpv import MPV as next_MPV
import youtube_dl

ydl = youtube_dl.YoutubeDL()

class MPV(next_MPV):
    def __init__(self):
        self.default_argv += (
            [ '--keep-open'
            , '--force-window'
            ])
        super().__init__(debug=True)

    def play(self, url):
        self.command("loadfile", path)
        self.set_property("pause", False)
    
    @staticmethod
    def fetchTitle(url):
        return ydl.extract_info(url, download=False).get('title')

mpv = MPV()