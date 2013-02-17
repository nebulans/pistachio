#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygtk
pygtk.require ("2.0")
import gtk
import gobject
gobject.threads_init ()


from interface import Window
from mixer import SourceMixer
from controller.keyboard import KeyboardController


resolution = (1200,800)


class Main:

	def __init__(self):
		
		self.window = Window("My Title", resolution)
		
		self.mixer = SourceMixer(self.window)
		self.mixer.addSource("im1", "image", location="../media/graph.png", resolution=resolution, alpha=0)
		self.mixer.addSource("im2", "image", location="../media/pic.jpg", resolution=resolution, alpha=0)
		self.mixer.addSource("white", "pattern", pattern=3, resolution=resolution, alpha=0)
		self.player = self.mixer.pipeline

		# Attach mixer to window for shutdown control
		self.window.mixer = self.mixer
		
		# Set up keyboard controller
		keyboardControl = KeyboardController(mixer=self.mixer, window=self.window)
		self.window.connect_event('key_press_event', keyboardControl.keypress)
		
		# Run pipeline and connect events
		self.mixer.start()

	

Main()
#gtk.gdk.threads_init()
gtk.main()
