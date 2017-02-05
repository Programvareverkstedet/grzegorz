import youtube_dl
from . import nyasync

@nyasync.ify
def title(url):
    ydl = youtube_dl.YoutubeDL()
    return ydl.extract_info(url, download=False).get('title')
