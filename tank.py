import math

from image_loader import image_loader
#from random import random, randint
import pygame
import os
#from block import Block
from config.config import Config
from config_game import DEATH_FIT, CAPTURE_ZONE_FIT, BG_SIZE
#from text import Text
from block import Block
#config = Config()
#print("config = Config()")


#tanks_images = [pygame.image.load(os.path.join(config.images_dir, "tanks", img)) for img in os.listdir(os.path.join(config.images_dir, "tanks"))]  # [pygame.image.load(f'images/tanks/tank_{i}.png').convert() for i in range(1, os.listdir())]
#print("tanks_images")
class Tank:
    tanks = []
    id_tank = 0

    def __init__(self, screen, name, keys=None, cords=(0, 0), size=4, speed=10, image=image_loader.load_tank_images()[0]):
        Tank.tanks.append(self)
        #image_loader = ImageLoader()

        #objects.append(self)

        self.type = "tank"
        Tank.id_tank += 1
        self.id_tank = Tank.id_tank

        #self.point = 0
        #self.point_name = name
        #self.point_obj = None

        '''for point in points:
            if point.name == name:
                self.point = point.score
                self.point_name = point.name
                self.point_obj = point'''

        self.image_rect = image.get_rect()

        self.x = cords[0]
        self.y = cords[1]
        self.size = size
        self.width = size * self.image_rect.width
        self.height = size * self.image_rect.height #16
        self.screen = screen

        self.name = name

        self.score = 0

        self.distance = 0
        self.side_obj = 0
        self.capture_zone = None
        self.flag_collide_bullet_zone = True
        self.bullet_reward_zone = None
        self.bullet = None

        self.reward = 0

        self.time_alive_tank = 5
        self.tick_gun = 0



        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.tank = pygame.transform.scale(image, (self.rect.width, self.rect.height))

        # self.tank = pygame.transform.rotate(self.tank, 90*2)
        self.side_tank = "up"
        # self.rotate_tank = 0

        self.speed = speed

        self.flag = False
        self.flag_bullet_spawn = True
        self.flag_timer_reward = False
        #self.flag_move = False
        self.is_alive = True


        self.keyLEFT = keys[0]
        self.keyRIGHT = keys[1]
        self.keyUP = keys[2]
        self.keyDOWN = keys[3]
        self.keySHOT = keys[4]

        self.sides = {
            "right": 90,
            "left": 270,
            "up": 0,
            "down": 180
        }
        #print(f"left: {self.keyLEFT}")
        '''left 
        right
        up
        down'''
        '''left_degree = 90
        right_degree = 270
        up_degree = 0
        down_degree = 180'''

    def rotate(self, side):

        if side in self.sides:  # and side != self.side_tank
            self.tank = pygame.transform.rotate(self.tank, self.sides[self.side_tank] - self.sides[side])
            self.side_tank = side
        elif side == self.side_tank:
            pass
        else:
            pass
        #print(self.sides[self.side_tank])

    def gun(self):
        from bullet import Bullet
        self.bullet = Bullet(self.screen, self, self.side_tank, cords=(self.rect.x, self.rect.y),
                             size_tank=(self.rect.width, self.rect.height))
        # self.bullet.rotate(self.sides[self.side_tank])

        if self.flag_bullet_spawn:
            self.bullet.spawn(self.side_tank)
            self.flag_bullet_spawn = False

        # self.bullet.update(self.side_tank)
        # self.bullet.draw()

    '''def point_up(self):
        self.point += 1
        if self.point_obj:
            self.point_obj.update(self.point)'''

    def compute_distance(self, object):
        x1 = self.rect.center[0]
        x2 = object.rect.center[0]

        y1 = self.rect.center[1]
        y2 = object.rect.center[1]
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        #pygame.draw.line(self.screen, (0, 100, 0), (x1, y1), (x2, y2), 3)
        #print(distance)
        return distance

    def compute_side(self, object):
        x1 = self.rect.center[0]
        x2 = object.rect.center[0]

        y1 = self.rect.center[1]
        y2 = object.rect.center[1]

        return math.degrees(math.atan2(y2 - y1, x2 - x1))




    def get_data(self, capture_zone):
        import torch.nn.functional as F
        #from bullet import Bullet
        #return int(self.distance / 30)
        #print(bool(len(Bullet.bullets)))
        return [self.rect.center[0]/1200, self.rect.center[1]/800, capture_zone.rect.center[0]/1200, capture_zone.rect.center[1]/800] #, self.sides[self.side_tank]
                                                #[self.side_obj, self.distance]
                                                #[self.rect.center[0], self.rect.center[1], capture_zone.rect.center[0], capture_zone.rect.center[1]]
                                                #[self.rect.center[0]/1200, self.rect.center[1]/800, capture_zone.rect.center[0]/1200, capture_zone.rect.center[1]/800]
                                                #[self.rect.center[0], self.rect.center[1], capture_zone.rect.center[0], capture_zone.rect.center[1]]#[self.side_obj/38, self.distance/120]
                                                #[self.side_obj, self.distance],
                                                #[self.side_obj, min(1000, self.distance)]

    def update(self, keys):

        #sec_tick = ticks//1000
        #lolcal_sec = 0
        oldX, oldY = self.rect.topleft
        side = None
        if keys[self.keyLEFT]:
            side = "left"
            self.rect.x -= self.speed
        elif keys[self.keyRIGHT]:
            side = "right"
            self.rect.x += self.speed
        elif keys[self.keyUP]:
            side = "up"
            self.rect.y -= self.speed
        elif keys[self.keyDOWN]:
            side = "down"
            self.rect.y += self.speed

        if keys[self.keySHOT]:
            self.tick_gun += 1
            #print(self.tick_gun)


        if keys[self.keySHOT] and self.flag_bullet_spawn:#self.flag_bullet_spawn #self.tick_gun%10==0
            self.gun()
            self.flag_bullet_spawn = True
            self.reward += -1
            #self.tick_gun += 1
        '''elif not keys[self.keySHOT] and not self.flag_bullet_spawn:
            self.flag_bullet_spawn = True'''

        # self.gun()
        self.rotate(side)

        objects = Tank.tanks+Block.blocks
        for object in objects:
            if self != object and self.rect.colliderect(object.rect) and object.type == "tank":
                #self.rect.x, self.rect.y = oldX, oldY
                pass
                #self.rect.x, self.rect.y = -self.speed, -self.speed


            if object.type == "tank" and ((self.rect.x+self.width > BG_SIZE[0] or self.rect.x < 0) or (self.rect.y < 0 or self.rect.y+self.height > BG_SIZE[1])):
                #self.rect.x, self.rect.y = bg_size[0]-self.rect.x, bg_size[1]-self.rect.y
                #self.rect.x, self.rect.y = oldX, oldY
                self.reward += DEATH_FIT
                #self.is_alive = False
                #self.rect.x, self.rect.y = -self.speed, -self.speed
            if object.type == "wall" and self.rect.colliderect(object.rect):
                self.rect.x, self.rect.y = oldX, oldY
                #self.rect.x, self.rect.y = -self.speed, -self.speed
            if object.type == "capture_zone":
                self.distance = self.compute_distance(object)
                self.side_obj = self.compute_side(object)
                #print(self.side_obj)
                self.capture_zone = object
                #side = [s[0] for s in self.sides.items() if s[1] == self.side_obj]

                if self.rect.colliderect(object.rect):
                    object.collide()
                    self.reward = CAPTURE_ZONE_FIT
                    self.score += 1
                    self.flag_timer_reward = True

                    #timer_alive += 1

                    '''for text in Text.texts:
                        if text.name == "timer":
                            text.update_text(f"таймер: {timer_alive}")'''


                    #self.time_alive_tank += 5
                    #object.point_up(self)

                        #print(f"point: {self.point}")
                #self.speed += 1


            #print(id(tank))


        '''for bullet in bullets:
            if self.rect.colliderect(bullet.rect):
                tanks.remove(self)
                bullets.remove(bullet)'''

        '''if event.type == pygame.KEYDOWN:
            self.flag = True
        if event.type == pygame.KEYUP:
            self.flag = False
        print(self.flag)
        if self.flag and pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self._rotate("up")
                self.rect.y -= self.speed
            elif event.key == pygame.K_DOWN:
                self._rotate("down")
                self.rect.y += self.speed
            elif event.key == pygame.K_LEFT:
                self._rotate("left")
                self.rect.x -= self.speed
            elif event.key == pygame.K_RIGHT:
                self._rotate("right")
                self.rect.x += self.speed'''

    def draw(self):
        self.screen.blit(self.tank, self.rect)
        # self.gun()


class TankNeiro(Tank):
    def __init__(self, screen, name, cords=(0, 0), size=4, image=None):
        super().__init__(screen, name, cords, size, image)
        # x = super()
        # print(x)

    def update(self, output_n):
        pass


