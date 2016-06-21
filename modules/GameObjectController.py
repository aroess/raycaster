#!/usr/local/bin/python
# -*- coding: utf-8 -*-

class GameObjectController(object):
	def __init__(self):
		self.objects = []

	def addObject(self, obj):
		self.objects.append(obj)

	def computeValues(self):
		for obj in self.objects:
			pass

	def filterAlive(self):
		self.objects = [obj for obj in self.objects if obj.isAlive()]

	def sortReverse(self):
		self.objects.sort(key=lambda x: x.screenDist, reverse = True)

	def sort(self):
		self.objects.sort(key=lambda x: x.screenDist)

	def getPosValues(self):
		pos = []
		for obj in self.objects: 
			pos.append((obj.x, obj.y))
		return pos

