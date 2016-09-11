#!/usr/bin/env python3
import remi.gui as gui, random, os, time
from remi import start, App
from threading import Timer

class namespace(object): pass

#globals:
COLOR_BLUE = "rgb(33, 150, 243)"
COLOR_BLUE_SHADOW = "rgba(33, 150, 243, 0.75)"

class MyApp(App):
	def __init__(self, *args):
		res_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'res')
		super(MyApp, self).__init__(*args, static_paths=(res_path,))
		
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
		self.playback.slider.set_value(int(random.random()*100))
		
		self.playlist.table.from_2d_matrix([['#', 'Name', "length"],
		                                    ['1', 'Awesome song', "5:23"],
		                                    ['2', 'min kuk er saa hard', "2:56"],
		                                    ['3', 'spis meg', "90:01"],
		                                    ['3', "Slidervalue: %s" % self.playback.slider.get_value(), "0:00"]])
		
		mpv.step()
		mpv.get_queue()
		mpv.position()
		
		Timer(1, self.mainLoop).start()
	def playback_play(self): pass
	def playback_pause(self): pass
	def playback_next(self): pass
	def input_submit(self, value=None):
		if not value:
			value = self.input.field.get_text()
		
		print(value)
		self.input.field.set_text("")
		

# starts the webserver
start(MyApp, address="0.0.0.0", start_browser=False, multiple_instance=True)
