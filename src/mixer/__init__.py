# -*- coding: utf-8 -*-

import sys, os
import pygtk, gtk, gobject
import pygst
pygst.require("0.10")
import gst
import time

from utility import requireKwargs

class Source(object):
	layerIndex = 0
	lastElement = False
	hangingConnections = 0
	def __init__(self, parent, name, sourceType, **kwargs):
		self.parent = parent
		self.name = name
		# Add elements common to all sources
		if not requireKwargs(kwargs, ["resolution", "alpha"]):
			print "Incorrect arguments supplied"
			raise Exception()
		self.alpha = gst.element_factory_make("alpha", "%salpha"%name)
		self.alpha.set_property("alpha", kwargs["alpha"])
		self.scaleCaps = gst.Caps("video/x-raw-yuv, width=%i, height=%i"%(kwargs["resolution"][0],kwargs["resolution"][1]))
		self.scaleFilter = gst.element_factory_make("capsfilter", "%scaps"%name)
		self.scaleFilter.set_property("caps", self.scaleCaps)
		self.scaler = gst.element_factory_make("videoscale", "%sscale"%name)
		self.scaler.set_property("add-borders", False)
		
		self.rateCaps = gst.Caps("video/x-raw-yuv, framerate=30/1")
		self.rateFilter = gst.element_factory_make("capsfilter", "%sratecaps"%name)
		self.rateFilter.set_property("caps", self.rateCaps)
		self.rate = gst.element_factory_make("videorate", "%srate"%name)
		
		self.parent.pipeline.add(self.alpha, self.scaleFilter, self.scaler, self.rateFilter, self.rate)
		
		
		# Create holder for list of elements created
		self.elements = []
		# Add initial elements as required		
		if sourceType == "image":
			if not requireKwargs(kwargs, ["location"]):
				print "Incorrect arguments supplied"
				raise Exception()
			self.src = gst.element_factory_make("filesrc", "%ssrc"%name)
			self.src.set_property("location", kwargs["location"])
			self.decoder = gst.element_factory_make("decodebin", "%sdec|%scolspace"%(name, name))
			self.freeze = gst.element_factory_make("imagefreeze", "%sfreeze"%name)
			self.colorspace = gst.element_factory_make("ffmpegcolorspace", "%scolspace"%name)
			self.parent.pipeline.add(self.src, self.decoder, self.freeze, self.colorspace)
			gst.element_link_many(self.src, self.decoder)
			gst.element_link_many(self.colorspace, self.scaler, self.scaleFilter, self.freeze,  self.alpha, self.rateFilter)
			self.lastElement = self.rateFilter
			self.decoder.connect("new-decoded-pad", self.new_decoded_pad)
			self.hangingConnections += 1
			self.parent.asyncStart = True
		elif sourceType == "pattern":
			if not requireKwargs(kwargs, ["pattern"]):
				print "Incorrect arguments supplied"
				raise Exception()
			self.src = gst.element_factory_make("videotestsrc", "%ssrc"%name)
			self.src.set_property("pattern", kwargs["pattern"])
			self.parent.pipeline.add(self.src)
			gst.element_link_many(self.src, self.scaler, self.scaleFilter, self.alpha, self.rateFilter)
			self.lastElement = self.rateFilter	
	def setInitial(self):
		# Set initial clock value
		self.initialClock = self.alpha.get_clock().get_time()
	def setAlpha(self, value, time=0, start=0):
		self.control = gst.Controller(self.alpha, "alpha")
		self.control.set_interpolation_mode("alpha", gst.INTERPOLATE_LINEAR)
		t = start * gst.SECOND + self.alpha.get_clock().get_time() - self.parent.initialTimes[self.alpha.get_property("name")]
		self.control.set("alpha", t, self.alpha.get_property("alpha"))
		self.control.set("alpha", t + gst.SECOND * time + 1, value)
	def new_decoded_pad(self, dbin, pad, islast):
		decode = pad.get_parent()
		pipeline = decode.get_parent()
		nextName = decode.get_property("name").split("|")[1]
		n = pipeline.get_by_name(nextName)
		decode.link(n)
		self.hangingConnections -= 1
		self.parent.ready()
	

class SourceMixer(object):
	fade = True		# Flag for fade vs take
	fadeTime = 1.	# Crossfade time in seconds
	fadeSteps = 100	# Number of crossfade steps
	layerIndex = 0
	activeSource = False
	asyncStart = False	# Use async start to allow connections to decode to negotiate
	def __init__(self, window):
		self.window = window
		# Set up pipeline
		self.pipeline = gst.Pipeline("mixing")
		# Set up mixer -> display for pipeline
		self.mixer = gst.element_factory_make("videomixer")
		self.mixer.set_property("background", "black")
		self.outConvert = gst.element_factory_make("ffmpegcolorspace")	# Removes alpha channel before displaying
		self.sink = gst.element_factory_make("autovideosink")
		self.pipeline.add(self.mixer, self.outConvert, self.sink)
		gst.element_link_many(self.mixer, self.outConvert, self.sink)
		# Create holder for sources
		self.sources = {}
		self.initialTimes = {}
	def addSource(self, name, sourceType, **kwargs):
		if not self.sources.get(name, False):
			self.sources[name] = Source(self, name, sourceType,  **kwargs)
			self.sources[name].lastElement.link(self.mixer)
			self.sources[name].layerIndex = self.layerIndex
			self.layerIndex += 1
		else:
			print "Source with that name already exists, not overwritten"
	def start(self):
		self.bus = self.pipeline.get_bus()
		self.bus.add_signal_watch()
		self.bus.enable_sync_message_emission()
		self.bus.connect("message", self.on_message)
		self.bus.connect("sync-message::element", self.on_sync_message)
		
		if self.asyncStart:
			self.pipeline.set_state(gst.STATE_PAUSED)
		else:
			self.pipeline.set_state(gst.STATE_PLAYING)
	def ready(self):
		ready = True
		for s in self.sources.keys():
			if self.sources[s].hangingConnections > 0:
				ready = False
		if ready:
			self.pipeline.set_state(gst.STATE_PLAYING)
	
	def setSource(self, source):
		#print self.activeSource
		if source == None:
			# Fade out active layer
			if self.activeSource:
				self.sources[self.activeSource].setAlpha(0, self.fadeTime)
				self.activeSource = False
		elif source in self.sources.keys():
			if source == self.activeSource:
				return
			if self.activeSource:
				# determine top layer
				if self.sources[self.activeSource].layerIndex > self.sources[source].layerIndex:
					# Current active layer on top
					self.sources[source].setAlpha(1)
					self.sources[self.activeSource].setAlpha(0, self.fadeTime)
				else:
					# New layer on top
					self.sources[source].setAlpha(1, self.fadeTime)
					self.sources[self.activeSource].setAlpha(0, 0, self.fadeTime)
				self.activeSource = source
			else:
				self.sources[source].setAlpha(1, self.fadeTime*2)
				self.activeSource = source			
	def setInitial(self, element, time):
		if not self.initialTimes.get(element, False):
			self.initialTimes[element] = time
	def on_message(self, bus, message):
		t = message.type
		if t == gst.MESSAGE_EOS:
			self.player.set_state(gst.STATE_NULL)
			print message
		elif t == gst.MESSAGE_ERROR:
			err, debug = message.parse_error()
			print "Error: %s" % err, debug
			self.pipeline.set_state(gst.STATE_NULL)
			print message
		elif t == gst.MESSAGE_STATE_CHANGED:
			if message.src.get_clock():
				self.setInitial(message.src.get_property("name"), message.src.get_clock().get_time())
	def on_sync_message(self, bus, message):	
		if message.structure is None:
			return
		message_name = message.structure.get_name()
		if message_name == "prepare-xwindow-id":
			# Assign the viewport
			imagesink = message.src
			imagesink.set_property("force-aspect-ratio", True)
			imagesink.set_xwindow_id(self.window.movie_window.window.xid)
