import remi.gui as gui
from remi import start, App

class MyApp(App):
	def __init__(self, *args):
		super(MyApp, self).__init__(*args)
		self.pressed = 0
	def main(self):
		topContainer = gui.HBox()
		container = gui.VBox(width=768)
		topContainer.append(container)
		#playback controls
		
		
		#playlist
		
		self.lbl = gui.Label('Hello world!')
		self.bt = gui.Button('Press me!')
		self.asdasd = gui.TextInput(hiehgt=30)
		
		
		# setting the listener for the onclick event of the button
		self.bt.set_on_click_listener(self, 'on_button_pressed')
		
		# appending a widget to another, the first argument is a string key
		container.append(self.lbl)
		container.append(self.bt)
		container.append(self.asdasd)
		
		# returning the root widget
		return container
		
	# listener function
	def on_button_pressed(self):
		self.pressed += 1
		self.lbl.set_text('Button pressed %i times!' % self.pressed)
		

# starts the webserver
start(MyApp, address="0.0.0.0", start_browser=False, multiple_instance=True)
