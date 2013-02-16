# -*- coding: utf-8 -*-

import sys, os
import pygtk, gtk, gobject
import pygst
pygst.require("0.10")
import gst
import time

from utility import requireKwargs

class Controller(object):
	def __init__(self, *args, **kwargs):
		if not requireKwargs(kwargs, ["mixer", "window"]):
			print "Controller base kwargs not found"
			raise Exception()
		self.mixer = kwargs["mixer"]
		self.window = kwargs["window"]
