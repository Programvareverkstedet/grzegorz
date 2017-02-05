#!/usr/bin/env python3
import remi.gui as gui, random, os, time, shutil, sys
from remi import start, App
from threading import Timer
if sys.version_info[0] == 2:
	from ConfigParser import ConfigParser
else:
	from configparser import ConfigParser
if "--no-mpv" not in sys.argv:
	from mpv_control import mpv

class namespace(object): pass

#globals:
COLOR_BLUE = "rgb(33, 150, 243)"
COLOR_BLUE_SHADOW = "rgba(33, 150, 243, 0.75)"


#todo: move this functionality to mpv_control.py or its own file, managing playlists and shit?
import youtube_dl
def get_youtube_metadata(url, ydl = youtube_dl.YoutubeDL()):
	#todo: check if url is valid
	
	#todo, stop it from doung the whole playlist
	resp = ydl.extract_info(url, download=False)
	#print resp.keys()
	
	title = resp.get('title')
	length = resp.get('duration')
	
	#print( title, "%i:%.2i" % (length//60, length%60))
	return title, "%i:%.2i" % (length//60, length%60)


class MyApp(App):
	def __init__(self, *args):
		res_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'res')
		super(MyApp, self).__init__(*args, static_paths=(res_path,))
		
		
		#initalize mpv here?
		
	def main(self):
		container = gui.VBox(width=512)
		
		#logo:
		container.append(gui.Image('/res/logo.jpg', width=512))
		
		#playback controls
		playbackContainer = gui.HBox()#; container.append(playbackContainer)
		self.playback = namespace()
		for i in ("play", "pause", "next"):
			button = gui.Button(i.capitalize(), margin="5px")
			setattr(self.playback, i, button)
			playbackContainer.append(button)
			button.set_on_click_listener(self, 'playback_%s' % i)
		self.playback.playing = gui.Label("Now playing: None")
		self.playback.slider = gui.Slider(0, 0, 100, 1, width="85%", height=20, margin='10px')
		
		container.append(self.playback.playing)
		container.append(playbackContainer)
		container.append(self.playback.slider)
		
		#playlist
		self.playlist = namespace()
		self.playlist.table = gui.Table(width="100%", margin="10px")
		self.playlist.table.from_2d_matrix([['#', 'Name', "length"]])
		container.append(self.playlist.table)
		
		self.playlist.queue = []#[i] = [source, name, length]
		
		#input
		container.append(gui.Label("Add songs:"))
		inputContainer = gui.HBox(width=512)
		self.input = namespace()
		self.input.field = gui.TextInput(single_line=True, height="20px", margin="5px")
		self.input.field.style["border"] = "1px solid %s" % COLOR_BLUE
		self.input.field.style["box-shadow"] = "0px 0px 5px 0px %s" % COLOR_BLUE_SHADOW
		self.input.submit = gui.Button("Submit!", margin="5px")
		self.input.field.set_on_enter_listener(self, "input_submit")
		self.input.submit.set_on_click_listener(self, "input_submit")
		
		inputContainer.append(self.input.field)
		inputContainer.append(self.input.submit)
		container.append(inputContainer)
		
		#return the container
		self.mainLoop()
		return container
	def mainLoop(self):
		#self.playback.slider.get_value()
		
		self.playback_update()
		
		self.playlist.table.from_2d_matrix(self.playlist_update())
		
		Timer(1, self.mainLoop).start()
	def playback_play(self): pass
	def playback_pause(self): pass
	def playback_next(self):
		source, name, length = self.playlist.queue.pop(0)
		
		pass
		
	def input_submit(self, value=None):
		if not value:
			value = self.input.field.get_text()
		
		title, length =  get_youtube_metadata(value)
		
		self.input.field.set_text("")
	#playback steps:
	def playback_update(self):
		#talk to mpv, see wether the song is being played still
		if 0:#if done:
			self.playback_next()
			self.playback.slider.set_value(0)
		else:
			self.playback.slider.set_value(100)
		
		return
	def playlist_update(self):
		out = [['#', 'Name', "length"]]
		
		for i, (source, name, length) in enumerate(self.playlist.queue):
			out.append([str(i+1), name, length])
		
		return out

def main():
	if not os.path.exists("config.ini"):
		shutil.copyfile("default_config.ini", "config.ini")
	
	ini = ConfigParser()
	with open("config.ini", "r") as f:
		ini.readfp(f)
	
	host = ini.get("server", "host")
	port = ini.getint("server", "port")
	start_browser = ini.getboolean("server", "start_browser")
	multiple_instance = ini.getboolean("server", "multiple_instance")
	
	# starts the webserver
	start(MyApp, address=host, port=port, start_browser=start_browser, multiple_instance=multiple_instance)

if __name__ == "__main__":
		main()