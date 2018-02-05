#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from math import sin
from math import pi
from math import sqrt
from math import atan2
from copy import deepcopy
from random import shuffle
import pygame

rad2deg = 180/pi

class Enemy(object):
    def __init__(self, screen_scale, x, y, level, group):
        group.addObject(self)
        self.memberOf = group
        self.image = pygame.image.load("sprites/enemy.bmp")
        self.scale = 1
        self.image = self.image.convert()
        self.image.set_colorkey((255, 0, 255))

        self.imgFrames = []
        self.frame = 0

        self.x = x
        self.y = y

        self.HP = 100
        self.accuracy = 0.5
        self.visible = True

        # original Sprite width and height
        self.spriteW = 43.0
        self.spriteH = 57.0

        self.uniqueFrames = 6
        self.actionList = {
            "walk": (0,1,2,3)
           ,"stand" : (0,0)
           ,"shoot": (4,5,4)
        }
        self.actionState = "walk"

        self.relHeight = 0.8 # 1 = 64 = wall height
        # c = original sprite height * distance to projection pane
        self.c = self.spriteH * 277 * screen_scale * self.relHeight

        # width and height, top and left of the scaled image
        self.screenW = 0
        self.screenH = 0
        self.screenTop = 0
        self.screenLeft = 0
        self.screenDist = 0

        self.pathTable = []
        self.pathExclude = []
        self.wayPoint = (self.x, self.y)
        self.moveSpeed = 0

        self.levelTable = level.table

        for row in level.table:
            temp = []
            for col in row:
                if col > 0: temp.append(-1)
                else: temp.append(col)
            self.pathTable.append(temp)

    def computeScaling(self, player):
        DELTA_X = (self.x - player.x)
        DELTA_Y = (self.y - player.y)
        self.screenDist = sqrt(DELTA_X ** 2 + DELTA_Y ** 2) # Pythagoras
        angle = atan2(DELTA_Y, DELTA_X) * rad2deg

        self.screenH = self.c / self.screenDist
        self.scale = self.screenH / self.spriteH
        self.screenW = self.scale * self.spriteW
        return angle

    def scaleSprite(self):
        self.scaledImage = pygame.transform.scale( \
            self.image \
           ,(int(self.spriteW * self.uniqueFrames * self.scale) \
           , int(self.spriteH * self.scale)))
        self.imgFrames = []
        # for each frame store left value for pixmap, rect = (l,t,w,h)
        for i in self.actionList[self.actionState]:
            self.imgFrames.append(self.screenW * i)

    def computePosValues(self, screen, player, clock):
        angle = self.computeScaling(player)

        # defnine max height of enemy sprite
        if self.screenH > 650:
            self.screenH = 650
            self.scale = self.screenH / self.spriteH
            self.screenW = self.scale * self.spriteW

        self.scaleSprite()

        # Don't know why this works!
        angle = player.dir + angle
        if angle > 180: angle -= 360

        # half screen - (relative height to wall height * half screen height)
        # + (correction for up/down player movement)
        self.screenTop = (200 * screen.scale / 2) - \
                (self.relHeight * self.screenH / 2) + (36 - player.height)
        # half screen + angle times angle width in px (can be negative)
        # - half width of sprite
        self.screenLeft = ((320 * screen.scale / 2) + \
               (angle * (1 / screen.rayAngleStep) * screen.scale) - \
               (self.screenW / 2))

        if not self.actionState == "walk":
            return

        self.moveSpeed = 0.05 * clock.get_time()

        wayPointx, wayPointy = self.wayPoint
        wayPointx = (wayPointx << 6) + 32
        wayPointy = (wayPointy << 6) + 32

        def isPathCollision(x, y):
            # check for wall collision
            if self.levelTable[int(y) >> 6][int(x) >> 6] > 0:
                return True

            return False

        if abs(self.x - wayPointx) > 10: # no jitter
            if self.x < wayPointx:
                if not isPathCollision(self.x + self.moveSpeed, self.y):
                    self.x += self.moveSpeed
            elif self.x > wayPointx:
                if not isPathCollision(self.x - self.moveSpeed, self.y):
                    self.x -= self.moveSpeed

        if abs(self.y - wayPointy) > 10: # no jitter
            if self.y < wayPointy:
                if not isPathCollision(self.x, self.y + self.moveSpeed):
                    self.y += self.moveSpeed
            elif self.y > wayPointy:
                if not isPathCollision(self.x, self.y - self.moveSpeed):
                    self.y -= self.moveSpeed

    def draw(self, screen):
        if self.frame > len(self.actionList[self.actionState])-1:
            self.frame = 0

        count = 0
        for w in range(int(self.screenW)-1):
            index = int(self.screenLeft/screen.scale + w/screen.scale)
            try:
                if screen.distList[index] < self.screenDist:
                    continue # wall nearer than enemy
                else:
                    if self.screenLeft + w < 0:
                        continue # enemy not on screen
                    count += 1
                    rect = (self.imgFrames[self.frame] + w, 0, \
                        1, self.screenH)
                    screen.pyscreen.blit(self.scaledImage, \
                        (self.screenLeft + w, self.screenTop), \
                        (self.imgFrames[self.frame] + w, 0, \
                            1, self.screenH))
            except IndexError:
                continue # enemy not on screen

        # drew more than 50% of the sprite -> visible
        if count/self.screenW > 0.5:
            self.visible = True
        else:
            self.visible = False

    def computeAction(self):
        # AI goes here
        if self.screenDist < 200 and self.visible:
            self.actionState = "shoot"
        else:
            self.actionState = "walk"

    def checkHit(self, screen, sound):
        if not self.visible: return
        middleOfScreen = 160 * screen.scale
        if self.screenLeft < middleOfScreen and \
        middleOfScreen < self.screenLeft + self.screenW:
            # compute damage
            if self.screenDist < 200:
                self.HP -= 100
            else:
                self.HP -= 50

            # emit sound
            if self.isAlive():
                sound.soundEffect("grunt")
            else:
                sound.soundEffect("death")

            return True

        return False

    def isAlive(self):
        if self.HP <= 0:
            return False
        else:
            return True

    def changeFrame(self):
        if self.frame < len(self.imgFrames)-1:
            self.frame += 1
        else:
            self.frame = 0

    def isCollision(self, x, y):
        if not self.visible: return False
        if self.screenDist < 24: return True
        return False

    def calcPath(self, player, exclude):

        def neighbors(x,y):
            # would pass through "diagonal wall"
            return [(x+1,y),(x-1,y),(x,y+1),(x,y-1)] #w,(x-1,y+1),(x+1,y+1),(x+1,y-1),(x-1,y-1)]

        def filterValid(neighbors):
            valid = []
            for n in neighbors:
                if pathTableCopy[n[1]][n[0]] == 0:
                    valid.append(n)
            return valid

        def calcDist(start):
            queue = []
            x, y = start

            pathTableCopy[y][x] = -1 # hide start point
            nextCells = filterValid(neighbors(x,y))
            queue += nextCells
            for x, y in nextCells: pathTableCopy[y][x] = 1

            while len(queue):
                next = queue.pop(0)
                x, y = next

                dist = pathTableCopy[y][x]
                nextCells = filterValid(neighbors(x,y))
                queue += nextCells
                for x, y in nextCells: pathTableCopy[y][x] = dist + 1

            x, y = start
            pathTableCopy[y][x] = 0

        def backtrack(point):
            x, y = point
            path = []

            for _ in range(pathTableCopy[y][x]):
                dist = pathTableCopy[y][x]
                ns = neighbors(x, y)
                shuffle(ns)
                for n in ns:
                    if pathTableCopy[n[1]][n[0]] == dist - 1:
                        path.append(n)
                        x, y = n
                        break
            return path

        def genPath(start, end):
            calcDist(start)
            return backtrack(end)

        def printTable():
            for row in pathTableCopy:
                for col in row:
                    if col == -1: print("xx", end="")
                    else:
                        if len(str(col)) == 1 : print(" "+str(col), end="")
                        else: print(col, end="")
                print()

        def makeGridPoint(x, y):
            return (int(x) >> 6, int(y) >> 6)

        # path tracing is backwards
        end = makeGridPoint(self.x, self.y)
        start = makeGridPoint(player.x, player.y)
        pathTableCopy = deepcopy(self.pathTable)

        pos = genPath(start, end)
        #printTable()
        if len(pos) > 2: self.wayPoint = pos[0]
