from urllib.parse import urlsplit, urlunsplit, parse_qs, urlencode
import youtube_dl
from youtube_dl.utils import DownloadError
from . import nyasync

@nyasync.ify
def title(url):
	ydl = youtube_dl.YoutubeDL()
	return ydl.extract_info(url, download=False).get('title')

def filter_query_params(url, allowed=[]):
	split_url = urlsplit(url)
	
	qs = parse_qs(split_url.query)
	print(qs)
	for key in list(qs.keys()):
		if key not in allowed:
			del qs[key]
	
	return urlunsplit((
		split_url.scheme,
		split_url.netloc,
		split_url.path,
		urlencode(qs, doseq=True),
		split_url.fragment,
		))

@nyasync.ify
def get_youtube_dl_metadata(url, ydl = youtube_dl.YoutubeDL()):
	if urlsplit(url).scheme == "":
		return None
	if urlsplit(url).netloc.lower() in ("www.youtube.com", "youtube.com", "youtub.be"):
		#Stop it from doing the whole playlist
		url = filter_query_params(url, allowed=["v"])
	if urlsplit(url).scheme == "ytdl":
		url = f"https://youtube.com/watch?v={urlsplit(url).netloc}"
	
	try:
		resp = ydl.extract_info(url, download=False)
	except DownloadError:
		return None
	
	#filter and return:
	return {k:v for k, v in resp.items() if k in
		("uploader", "title", "thumbnail", "description", "duration")}

async def get_metadata(url):
	data = await get_youtube_dl_metadata(url)
	if data is None:
		# (TODO): local ID3 tags
		return {"failed":True}
	
	return data
