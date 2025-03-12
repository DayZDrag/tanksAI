from random import randint

import pygame

from config_game import DARKENED_GREEN_COLOR, RED_COLOR, BG_SIZE
from text import Point


class Block:
    blocks = []
    def __init__(self, screen, cords, color=DARKENED_GREEN_COLOR, size=4):
        Block.blocks.append(self)
        #objects.append(self)

        self.type = None

        self.screen = screen
        self.x = cords[0]
        self.y = cords[1]

        self.color = color

        self.width = size * 16
        self.height = size * 16

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill(self.color)

    def draw(self):
        self.screen.blit(self.surface, self.rect)


class Wall(Block):
    def __init__(self, screen, cords, color=RED_COLOR, size=4):
        super().__init__(screen, cords, color, size)


        self.type = "wall"


class CaptureZone(Block):
    def __init__(self, screen, cords, color=DARKENED_GREEN_COLOR, size=4):
        super().__init__(screen, cords, color, size)

        self.screen = screen
        self.color = color

        self.type = "capture_zone"

    def point_up(self, object):
        if object.type == "tank":
            for point in Point.points:
                if point.name == object.name:
                    point.update(point.score+1)
                    break

    def collide(self):
        #print("you win!")
        #blocks.remove(self)
        self.rect.x = randint(0, BG_SIZE[0]-self.width)
        self.rect.y = randint(0, BG_SIZE[1]-self.height)
        #Wall(self.screen, (randint(0, bg_size[0]-self.width), randint(0, bg_size[1]-self.height)))