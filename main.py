import pygame

import sys
import os

import math

from random import choice, randint, random

import neat_agent

from block import CaptureZone, Block
from bullet import Bullet
from config.config import Config
from config_game import BG_SIZE, screen, TIME_FIT
from tank import Tank, tanks_images
from text import Text







# load images tanks


# print(tanks_images)
'''def create_rect():
    r = pygame.Rect(50, 50, 100, 200)
    pygame.draw.rect(screen, (255, 0, 0), r, 0)'''

'''x = 0
y = 0

def create_tank():
    height = width = 4*16
    rect = pygame.Rect(x, y, width, height)е
    tank = pygame.transform.scale(tanks_images[0], (rect.width, rect.height))
    #pygame.draw.rect(screen, ())
    #orig_rect = tank.get_rect()
    tank = pygame.transform.rotate(tank, 270)
    return tank
'''

#bullets = []

#tanks = []
#blocks = []
#objects = tanks+blocks







