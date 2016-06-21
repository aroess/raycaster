#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from math import tan
from math import cos
from math import sin
from math import pi

import pygame, os
from pygame.locals import *

deg2rad = pi/180

class ProjectionPlane(object):
    def __init__(self, table, scale):
        # init variables
        self.scale = scale
        # c = 64 (wall height) * 277 (Distance to projection plane)
        self.c = 17728 * self.scale
        self.rayAngleStep = 60/320.0

        self.table = table

        self.pyscreen = pygame.display.set_mode((320 * self.scale, 200 * self.scale))
        #self.pyscreen = pygame.display.set_mode((320 * self.scale, 200 * self.scale), FULLSCREEN | HWSURFACE | DOUBLEBUF)
        pygame.mouse.set_visible(False)

        self.textures = []
        self.prepareTextures()

        # store distances, which is nearer: enemy or wall?
        self.distList = []

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

    def horizontalIntersection(self, rayAngle, player_x, player_y, beta):
        if(rayAngle == 0):   return -1, -1, -1
        if(rayAngle == 180): return -1, -1, -1

        Y_COORD = int(player_y / 64) << 6

        if rayAngle > 0 and rayAngle < 180:
            Y_COORD -=   1    # Strahl zeigt nach oben
            DELTA_Y  = -64
            DELTA_X  =  64 / tan(rayAngle*deg2rad)
        else:
            Y_COORD +=  64    # Strahl zeigt nach unten
            DELTA_Y  =  64
            DELTA_X  = -64 / tan(rayAngle*deg2rad)

        X_COORD = player_x + (player_y - Y_COORD) / tan(rayAngle*deg2rad)

        if(rayAngle > 90 and rayAngle < 270): X_COORD += 1

        Y_INDEX = int(Y_COORD) >> 6
        X_INDEX = int(X_COORD) >> 6

        try:
            while(self.table[Y_INDEX][X_INDEX] == 0):
                Y_COORD += DELTA_Y
                X_COORD += DELTA_X
                Y_INDEX = int(Y_COORD) >> 6
                X_INDEX = int(X_COORD) >> 6
        except IndexError:
            return -1, -1, -1

        # compute correct offset
        if rayAngle < 180 and rayAngle > 0:
            offset = int(X_COORD % 64)
        else:
            offset = int(64 - X_COORD % 64)

        return abs(abs(player_y - Y_COORD)/sin(rayAngle*deg2rad)*cos(beta*deg2rad)) \
              ,offset \
              ,self.table[Y_INDEX][X_INDEX]

    def verticalIntersection(self, rayAngle, player_x, player_y, beta):
        if(rayAngle == 90):  return -1, -1, -1
        if(rayAngle == 270): return -1, -1, -1

        X_COORD = int(player_x / 64) << 6

        if rayAngle < 90 or rayAngle > 270:
            X_COORD +=  64  # Strahl zeigt nacht rechts
            DELTA_X  =  64
            DELTA_Y  = -64 * tan(rayAngle*deg2rad)
        else:
            X_COORD -=   1  # Strahl zeigt nach links
            DELTA_X  = -64
            DELTA_Y  =  64 * tan(rayAngle*deg2rad)

        Y_COORD = player_y + (player_x - X_COORD) * tan(rayAngle*deg2rad)

        if(rayAngle > 0 and rayAngle < 180): Y_COORD += 1

        Y_INDEX = int(Y_COORD) >> 6
        X_INDEX = int(X_COORD) >> 6

        try:
            while(self.table[Y_INDEX][X_INDEX] == 0):
                Y_COORD += DELTA_Y
                X_COORD += DELTA_X
                Y_INDEX = int(Y_COORD) >> 6
                X_INDEX = int(X_COORD) >> 6
        except IndexError:
            return -1, -1, -1

        # compute correct offset
        if rayAngle < 90 or rayAngle > 270:
            offset = int(Y_COORD % 64)
        else:
            offset = int(64 - Y_COORD % 64)

        return abs(abs(player_x-X_COORD)/cos(rayAngle*deg2rad)*cos(beta*deg2rad)) \
              ,offset \
              ,self.table[Y_INDEX][X_INDEX]

    def castRays(self, player):
        self.distList = []
        startFOV = player.dir + 30
        if(startFOV > 360): startFOV -= 360

        # background color = sky color
        self.pyscreen.fill((41 ,36, 33))

        for i in xrange(0,320):
            currentAngle = startFOV - i * self.rayAngleStep
            if currentAngle < 0:
                currentAngle = currentAngle + 360

            y, offsetY, textureIDy = self.horizontalIntersection( \
                currentAngle \
                ,player.x \
                ,player.y \
                ,30 - i * self.rayAngleStep)
            x, offsetX, textureIDx = self.verticalIntersection( \
                currentAngle \
               ,player.x \
               ,player.y \
               ,30 - i * self.rayAngleStep)

            if (x < y and x > 0) or (x > y and y < 1):
                dist = x
                offset = offsetX
                textureID = textureIDx
                alpha = 255
            else:
                dist = y
                offset = offsetY
                textureID = textureIDy
                alpha = 200

            height   = self.c / dist
            startPos = 100 * self.scale - height / 2  + (32 - player.height)
            endPos   = 100 * self.scale + height / 2  + (32 - player.height)

            slice = self.textures[textureID-1][offset-1]
            #texture transform
            #prevent short integer overflow
            if height > 65535: height = 65535
            slice = pygame.transform.scale(slice, (self.scale, int(height)))
            # walls in east/west direction should appear darker
            slice.set_alpha(alpha)
            # draw floor
            pygame.draw.line(self.pyscreen, (30, 30, 30), (i * self.scale, endPos),
                            (i * self.scale, 200 * self.scale), self.scale)

            # background color = sky color
            # draw slice
            self.pyscreen.blit(slice, (i * self.scale, startPos))

            self.distList.append(dist)
