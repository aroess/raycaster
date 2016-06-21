#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from math import tan
from math import cos
from math import sin
from math import pi

import pygame, os
from pygame.locals import *

from ctypes import *
# load the shared object
libtest = cdll.LoadLibrary('./engine/engine.so.1.0')

deg2rad = pi/180

class ProjectionPlane(object):
    def __init__(self, table, scale):
        # init variables
        self.scale = scale
        # c = 64 (wall height) * 277 (Distance to projection plane) 17728 11328
        self.c = 17728 * self.scale
        self.rayAngleStep = 60/320.0

        self.pyscreen = pygame.display.set_mode((320 * self.scale, 200 * self.scale))
        #self.pyscreen = pygame.display.set_mode((320 * self.scale, 200 * self.scale), FULLSCREEN | HWSURFACE | DOUBLEBUF)
        pygame.mouse.set_visible(False)

        self.textures = []
        self.prepareTextures()

        # store distances, which is nearer: enemy or wall?
        self.distList = []

        # reshape 2-dim array to 1-dim array
        arr = []
        for row in table:
            for elem in row: arr.append(elem)

        self.tableH = len(table)
        self.tableW = len(table[0])
        # overwrite 2-dim table
        self.table = (c_int * len(arr))(*arr)


    def prepareTextures(self):
        files = os.listdir("textures")
        files.sort()
        for i in range(len(files)):
            newTexture = pygame.image.load(os.path.join("textures", files[i]))
            newTexture = newTexture.convert()
            textureArray = []
            for j in range(64):
                #chop left side
                slice = pygame.transform.chop(newTexture, (0, 0, j, 0))
                #chop right side
                slice = pygame.transform.chop(slice, (1, 0, 64, 0))
                #save slice in temporary array
                textureArray.append(slice)
            # append slice to textures array
            self.textures.append(textureArray)


    def castRays(self, player):
        self.distList = []
        array_function_handler = libtest.render
        array_function_handler.restype = POINTER(c_float)
        array = array_function_handler(self.table, self.tableH, \
            self.tableW, c_float(player.x), c_float(player.y), \
            c_int(int(player.dir)))

        self.distList = [array[i] for i in xrange(0, 320*4, 4)]
        off   = [int(array[i]) for i in xrange(1, 320*4+1, 4)]
        tex   = [int(array[i]) for i in xrange(2, 320*4+2, 4)]
        alpha = [int(array[i]) for i in xrange(3, 320*4+3, 4)]

        # background color = sky color
        self.pyscreen.fill((41 ,36, 33))

        for i in xrange(0,320):

            height   = self.c / self.distList[i]
            startPos = 100 * self.scale - height / 2  + (32 - player.height)
            endPos   = 100 * self.scale + height / 2  + (32 - player.height)

            slice = self.textures[tex[i]-1][off[i]-1]

            #prevent short integer overflow
            if height > 65535: height = 65535
            slice = pygame.transform.scale(slice, (self.scale, int(height)))
            # walls in east/west direction should appear darker
            slice.set_alpha(alpha[i])
            #draw floor
            pygame.draw.line(self.pyscreen, (30, 30, 30), (i * self.scale, endPos),
                            (i * self.scale, 200 * self.scale), self.scale)

            ##draw sky
            #pygame.draw.line(self.pyscreen, (41 ,36, 33), (i * self.scale,0),
            #                (i * self.scale, startPos), self.scale)

            #draw slice
            self.pyscreen.blit(slice, (i * self.scale, startPos))
