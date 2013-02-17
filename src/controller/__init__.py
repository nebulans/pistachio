# -*- coding: utf-8 -*-

from utility import requireKwargs

class Controller(object):
	def __init__(self, *args, **kwargs):
		if not requireKwargs(kwargs, ["mixer", "window"]):
			print "Controller base kwargs not found"
			raise Exception()
		self.mixer = kwargs["mixer"]
		self.window = kwargs["window"]
