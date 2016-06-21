#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import pygame

class GameSound(object):
    def __init__(self):
        self.freq = 22050
        self.bitsize = -16   # unsigned 16 bit
        self.channels = 2    # 1 is mono, 2 is stereo
        self.buffer = 1024   # number of samples
        self.volume = 0.3    # float between 0.0 and 1.0

        self.effect = {}
        self.effect["shotgun"] = pygame.mixer.Sound('sounds/shotgun.ogg')
        self.effect["grunt"] = pygame.mixer.Sound('sounds/grunt.ogg')
        self.effect["death"] = pygame.mixer.Sound('sounds/death.ogg')

        self.effect["shotgun"].set_volume(0.4)
        self.effect["grunt"].set_volume(0.3)
        self.effect["death"].set_volume(0.2)

    def backgroundMusic(self):
        pygame.mixer.music.load("sounds/bgmusic.mp3")
        pygame.mixer.init(self.freq, self.bitsize, self.channels, self.buffer)
        pygame.mixer.music.set_volume(self.volume)
        # endless loop
        pygame.mixer.music.play(-1)

    def soundEffect(self, etype):
        self.effect[etype].play()
