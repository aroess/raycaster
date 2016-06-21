#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import argparse
parser = argparse.ArgumentParser(description='Python Raycaster.')
parser.add_argument('--scale', nargs='?', type=int, default=2,
                    help='screen scaling, (Resolution 320X*200X) Default: 2, Max:10')
parser.add_argument('--fast', action='store_true',
                    help='use ctypes interface (Linux/x64 only).')
parser.add_argument('--cap', nargs='?', default=30, type=float,
                    help='FPS Cap. Default:30, Disable:0.')
args = parser.parse_args()

import modules.GameLevel as GameLevel
import modules.FPSPlayer as FPSPlayer
if args.fast:
    import modules.ProjectionPlaneFast as ProjectionPlane
else:
    import modules.ProjectionPlane as ProjectionPlane
import modules.GameObjectController as GameObjectController
import modules.GameSound as GameSound
import modules.Enemy as Enemy
import modules.Weapon as Weapon
import modules.Events as Events

import pygame
from pygame.locals import *

pygame.init()
pygame.display.set_caption("Raycaster")

level = GameLevel.GameLevel("levels/level1.txt")
player = FPSPlayer.FPSPlayer(236, 312, 0, level.table)
if args.scale < 0: args.scale = 1
if args.scale > 10: args.scale = 10
screen = ProjectionPlane.ProjectionPlane(level.table, args.scale)
weapon = Weapon.Weapon(screen.scale)
sound = GameSound.GameSound()
clock = pygame.time.Clock()
customEvents = Events.Events()

enemyGroup = GameObjectController.GameObjectController()
Enemy.Enemy(screen.scale, 1120, 320, level, enemyGroup)
Enemy.Enemy(screen.scale, 1120, 420, level, enemyGroup)
Enemy.Enemy(screen.scale, 1120, 220, level, enemyGroup)
Enemy.Enemy(screen.scale, 1120, 520, level, enemyGroup)
Enemy.Enemy(screen.scale, 1120, 150, level, enemyGroup)

pygame.time.set_timer(USEREVENT+1, 10)
sound.backgroundMusic()
myfont = pygame.font.SysFont(None, 15)
label = None

# Game loop
while 1:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            raise SystemExit

        if event.type == USEREVENT+1:
            customEvents.processGameEvents(enemyGroup, weapon, player)

        if event.type == KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                raise SystemExit

        if event.type == KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                player.lastInput.clear()
                player.acc = 1

    screen.castRays(player)

    for obj in enemyGroup.objects:
        obj.computePosValues(screen, player, clock)
        obj.computeAction()
        obj.draw(screen)

    player.action(pygame.key.get_pressed(), weapon, enemyGroup, screen, clock, sound)

    enemyGroup.sortReverse()
    enemyGroup.filterAlive()

    weapon.draw(screen)

    label = myfont.render(str(clock.get_fps()), 1, (255,255,0))
    screen.pyscreen.blit(label, (10, 10))

    pygame.display.flip()
    pygame.event.pump()
    clock.tick(args.cap)
