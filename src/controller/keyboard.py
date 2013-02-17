# -*- coding: utf-8 -*-


import pygtk
pygtk.require ("2.0")
import gtk


from controller import Controller

class KeyboardController(Controller):
	def __init__(self, *args, **kwargs):
		super(KeyboardController, self).__init__(*args, **kwargs)
	def keypress(self, widget, event):
		keyname = gtk.gdk.keyval_name(event.keyval)
		if keyname == "q":
			self.window.quit()
		elif keyname == "f":
			self.window.setFullscreen(None, True)
		elif keyname == "KP_8":
			self.mixer.setSource(None)
		elif keyname == "KP_5":
			self.mixer.setSource("im1")
		elif keyname == "KP_6":
			self.mixer.setSource("im2")
		elif keyname == "KP_2":
			self.mixer.setSource("white")
		elif keyname == "KP_0":
			print "Toggle"
			self.mixer.toggleFade()
		else:
			print keyname
