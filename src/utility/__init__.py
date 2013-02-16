# -*- coding: utf-8 -*-

def requireKwargs(kwargs, requirements):
	for r in requirements:
		if not r in kwargs.keys():
			print "Missing key %s"%r
			return False
	return True
