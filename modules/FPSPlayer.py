#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from math import cos
from math import sin
from math import pi
from collections import deque
import pygame

deg2rad = pi/180

class FPSPlayer(object):
    def __init__(self, x, y, dir, level):
        self.x = x
        self.y = y
        self.dir = dir
        self.moveSpeed = 8
        self.turnSpeed = 4
        self.HP = 100
        self.height = 32
        self.UP = True

        self.level = level

        self.lastInput = deque((0, 1)*50, 100)
        self.acc = 1

    def isCollision(self, x, y):
        X_COORD = int(x) >> 6
        Y_COORD = int(y) >> 6
        return self.level[Y_COORD][X_COORD]

    def wallSlide(self):
        if self.dir > 0 and self.dir < 90:
            # wall top
            if self.isCollision(self.x, self.y-32) and \
            not self.isCollision(self.x+32, self.y):
                self.x += self.moveSpeed
            # wall right
            if self.isCollision(self.x+32, self.y) and \
            not self.isCollision(self.x, self.y-32):
                self.y -= self.moveSpeed
        if self.dir > 90 and self.dir < 180:
            # wall top
            if self.isCollision(self.x, self.y-32) and \
            not self.isCollision(self.x-32, self.y):
                self.x -= self.moveSpeed
            # wall left
            if self.isCollision(self.x-32, self.y) and \
            not self.isCollision(self.x, self.y-32):
                self.y -= self.moveSpeed
                self.y -= self.moveSpeed
        if self.dir > 180 and self.dir < 270:
            # wall bottom
            if self.isCollision(self.x, self.y+32) and \
            not self.isCollision(self.x-32, self.y):
                self.x -= self.moveSpeed
            # wall left
            if self.isCollision(self.x-32, self.y) and \
            not self.isCollision(self.x, self.y+32):
                self.y += self.moveSpeed
        if self.dir > 270 and self.dir < 360:
            # wall bottom
            if self.isCollision(self.x, self.y+32) and \
            not self.isCollision(self.x+32, self.y):
                self.x += self.moveSpeed
            # wall left
            if self.isCollision(self.x+32, self.y) and \
            not self.isCollision(self.x, self.y+32):
                self.y += self.moveSpeed

    def changeHeight(self, clock):
        if self.UP and self.height < 44:
            self.height = self.height + 0.1 * clock.get_time()
        elif self.UP and self.height > 44:
            self.UP = False

        if not self.UP and self.height > 18:
            self.height = self.height - 0.1 * clock.get_time()
        elif not self.UP and self.height < 18:
            self.UP = True

    def action(self, key_pressed, weapon, enemyGroup, screen, clock, sound):

        self.moveSpeed = 0.4 * clock.get_time()
        # Probleme  wenn self.dir float wird?
        self.turnSpeed = 0.1 * clock.get_time()
        fps = int(clock.get_fps()) / 4
        if list(self.lastInput)[-fps:].count(0) == fps or \
           list(self.lastInput)[-fps:].count(1) == fps:
            if self.acc < 3: self.acc += 0.1
            self.turnSpeed *= self.acc

        if key_pressed[pygame.K_LEFT]:
            self.lastInput.append(0)
            self.dir = (self.dir + self.turnSpeed) % 360

        if key_pressed[pygame.K_RIGHT]:
            self.lastInput.append(1)
            self.dir = (360 + self.dir - self.turnSpeed) % 360

        if key_pressed[pygame.K_w]:
            self.changeHeight(clock)
            weapon.sway(clock)
            if self.dir == 0:
                newX = self.x + self.moveSpeed
                newY = self.y
            elif self.dir == 180:
                newX = self.x - self.moveSpeed
                newY = self.y
            else:
                newY = self.y - sin(self.dir*deg2rad) * self.moveSpeed
                newX = self.x + cos(self.dir*deg2rad) * self.moveSpeed

            enemyCollision = False
            for obj in enemyGroup.objects:
                enemyCollision = obj.isCollision(newX, newY)

            if not self.isCollision(newX, newY) and not enemyCollision:
                self.x = newX
                self.y = newY
            else:
                self.wallSlide()

        if key_pressed[pygame.K_s]:
            self.changeHeight(clock)
            weapon.sway(clock)
            if self.dir == 0:
                newX = self.x - self.moveSpeed
                newY = self.y
            elif self.dir == 180:
                newX = self.x + self.moveSpeed
                newY = self.y
            else:
                newY = self.y + sin(self.dir*deg2rad) * self.moveSpeed
                newX = self.x - cos(self.dir*deg2rad) * self.moveSpeed

            if self.isCollision(newX, newY) == False:
                self.x = newX
                self.y = newY

        if key_pressed[pygame.K_a]:
            weapon.sway(clock)
            if self.dir == 0:
                newY = self.y - self.moveSpeed
                newX = self.x
            elif self.dir == 180:
                newY = self.y + self.moveSpeed
                newX = self.x
            else:
                newX = self.x - sin(self.dir * deg2rad) * self.moveSpeed
                newY = self.y - cos(self.dir * deg2rad) * self.moveSpeed

            if self.isCollision(newX, newY) == False:
                self.x = newX
                self.y = newY

        if key_pressed[pygame.K_d]:
            weapon.sway(clock)
            if self.dir == 0:
                newY = self.y + self.moveSpeed
                newX = self.x
            elif self.dir == 180:
                newY = self.y - self.moveSpeed
                newX = self.x
            else:
                newX = self.x + sin(self.dir * deg2rad) * self.moveSpeed
                newY = self.y + cos(self.dir * deg2rad) * self.moveSpeed

            if self.isCollision(newX, newY) == False:
                self.x = newX
                self.y = newY

        if key_pressed[pygame.K_SPACE]:
            if weapon.animation: return
            weapon.shoot(sound)
            enemyGroup.sort()
            hit = False
            for obj in enemyGroup.objects:
                hit = obj.checkHit(screen, sound)
                # only hit nearest enemy
                if hit: break
