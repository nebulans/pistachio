#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os
import pygtk, gtk, gobject
import pygst
pygst.require("0.10")
import gst
import time

from interface import Window
from mixer import Source, SourceMixer
from controller.keyboard import KeyboardController
from utility import requireKwargs


resolution = (1200,800)


class Main:

	def __init__(self):
		
		self.window = Window("My Title", resolution)
		
		self.mixer = SourceMixer(self.window)
		self.mixer.addSource("im1", "image", location="../graph.png", resolution=resolution, alpha=0)
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
gtk.gdk.threads_init()
gtk.main()
