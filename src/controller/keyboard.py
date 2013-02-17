# -*- coding: utf-8 -*-

import sys, os
import pygtk, gtk, gobject
import pygst
pygst.require("0.10")
import gst
import time

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
		else:
			print keyname
