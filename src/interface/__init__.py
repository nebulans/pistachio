# -*- coding: utf-8 -*-

import pygtk
pygtk.require ("2.0")
import gtk
import pygst
pygst.require("0.10")
import gst

class Window:
	mixer = False
	def __init__(self, title, resolution):
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_title(title)
		self.window.set_default_size(resolution[0],resolution[1])
		self.window.connect("destroy", self.quit)
		self.window.connect("realize", self.realize_cb)
		self.vbox = gtk.VBox()
		self.window.add(self.vbox)
		self.movie_window = gtk.DrawingArea()
		self.vbox.add(self.movie_window)
		self.window.show_all()
		self.fullscreen = False
	def quit(self, widget=None, data=None):
		if self.mixer:
			self.mixer.pipeline.set_state(gst.STATE_NULL)
		gtk.main_quit()
	def connect_event(self, event, callback):
		self.window.connect(event, callback)
	def realize_cb(self, widget):
		# Hide mouse pointer in window
		pixmap = gtk.gdk.Pixmap(None, 1, 1, 1)
		color = gtk.gdk.Color()
		cursor = gtk.gdk.Cursor(pixmap, pixmap, color, color, 0, 0)
		widget.window.set_cursor(cursor)
	def setFullscreen(self, value, toggle=False):
		if toggle:
			value = self.fullscreen == False
		if value == True:
			self.window.fullscreen()
			self.fullscreen = True
		else:
			self.window.unfullscreen()
			self.fullscreen = False
