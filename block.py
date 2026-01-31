from random import randint

import pygame
from icecream import ic

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
        self.surface.fill(self.color)
        self.screen.blit(self.surface, self.rect)


class Wall(Block):
    walls_list = []
    def __init__(self, screen, cords, color=RED_COLOR, size=4):
        super().__init__(screen, cords, color, size)
        Wall.walls_list.append(self)


        self.type = "wall"

    def update(self):
        self.new_pos()
        from tank import Tank
        for obj in Tank.tanks + Block.blocks:
            if (obj is self):
                continue
            if obj.rect.colliderect(self.rect):
                self.update()



    def new_pos(self):
        self.rect.x = randint(1, BG_SIZE[0]//self.width)*self.width-self.width
        self.rect.y = randint(1, BG_SIZE[1]//self.height)*self.height-self.height




class CaptureZone(Block):
    capture_zone_list = []
    def __init__(self, screen, cords, color=DARKENED_GREEN_COLOR, size=4):
        super().__init__(screen, cords, color, size)

        CaptureZone.capture_zone_list.append(self)

        self.screen = screen
        self.color = color

        self.type = "capture_zone"
        self.collide()



        from tank import Tank
        '''for obj in Tank.tanks + Block.blocks:
            for wall in Block.blocks:

                if not (wall.type=="wall") or (wall is obj): #
                    continue

                if obj.rect.colliderect(wall.rect):
                    wall.new_pos()'''




    def point_up(self, object):
        if object.type == "tank":
            for point in Point.points:
                if point.name == object.name:
                    point.update(point.score+1)
                    break

    def collide(self):
        #print("you win!")
        #blocks.remove(self)


        self.new_pos()
        from tank import Tank
        for obj in Tank.tanks + Block.blocks:
            if (obj is self):
                continue
            if obj.rect.colliderect(self.rect):
                self.collide()

        """for wall in Wall.walls_list:
            wall.update()"""



    def new_pos(self):
        self.rect.x = randint(0, BG_SIZE[0] - self.width)
        self.rect.y = randint(0, BG_SIZE[1] - self.height)


    def new_pos_grid(self):
        self.rect.x = randint(1, BG_SIZE[0]//self.width)*self.width-self.width
        self.rect.y = randint(1, BG_SIZE[1]//self.height)*self.height-self.height



    def draw(self):
        self.color = DARKENED_GREEN_COLOR
        self.surface.fill(self.color)
        self.screen.blit(self.surface, self.rect)

