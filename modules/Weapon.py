#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from math import cos 
from math import sin
from math import pi 
import pygame

class Weapon(pygame.sprite.Sprite):
    def __init__(self, screen_scale):
        self.ammo = 10
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("sprites/shotgun.bmp")
        self.scale = 1
        self.image = self.image.convert()
        self.image.set_colorkey((255, 255, 255))

        self.imgFrames = []
        self.frame = 0

        self.spriteW = 190.0
        self.spriteH = 130.0
        self.uniqueFrames = 11

        self.top = 115 + 5 * cos(0);
        self.left = 130 + 10 * sin(0.8)
        self.swayParam = 0
        
        self.scale = 0.75 * screen_scale
        self.image = pygame.transform.scale(self.image \
           ,(int(self.spriteW * self.uniqueFrames * self.scale) \
           ,int(self.spriteH * self.scale)))
        width  = int(self.spriteW * self.scale)
        height = int(self.spriteH * self.scale)
        for i in xrange(self.uniqueFrames):
            self.imgFrames.append((width * i, 0, width, height))

        self.animation = False

    def changeFrame(self):
        if not self.animation: return
        if self.frame < len(self.imgFrames)-1: 
            self.frame += 1 
        else:
            self.frame = 0
            self.animation = False

    def sway(self, clock):
        self.swayParam += clock.get_time() * 0.005
        if self.swayParam > pi * 2: t = 0
        self.left = 130 + 10 * sin(self.swayParam + 0.8);           
        self.top = 115 + 5 * cos(2 * self.swayParam);        

    def draw(self, screen):
        screen.pyscreen.blit(self.image, (self.left * screen.scale, \
            self.top * screen.scale), self.imgFrames[self.frame])

    def shoot(self, sound):
        #if self.animation: return
        sound.soundEffect("shotgun")
        self.animation = True
        self.ammo -= 1

