#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import pygame

class Events(object):
    def __init__(self):
    	self.times = 0

    def processGameEvents(self, enemyGroup, weapon, player):

        if self.times % 8 == 0: # every 80ms
            weapon.changeFrame()

        if self.times % 40 == 0: # every 400ms
            for obj in enemyGroup.objects:
                obj.changeFrame()
                obj.computeScaling(player)

        if self.times % 150 == 0: # every 1500ms
             for obj in enemyGroup.objects:
                 obj.calcPath(player, enemyGroup.getPosValues())

        self.times += 1
        # max timer 10ms * 100 = 1sec => 10secs
        if self.times == 10000: self.times = 1
