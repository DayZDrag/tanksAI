import pygame

from config_game import BG_SIZE
from tank import Tank
from block import Block
class Bullet:
    bullets = []
    def __init__(self, screen, tank, side_tank, cords, size_tank, size=(20, 20), color=(255, 255, 255)):
        self.width = size[0]
        self.height = size[1]

        Bullet.bullets.append(self)
        self.tank = tank

        self.radius = size[0] / 2

        self.x = cords[0]
        self.y = cords[1]

        self.tank_width = size_tank[0]
        self.tank_height = size_tank[1]

        self.side_tank = side_tank

        self.color = color
        self.speed = 15

        self.screen = screen

        self.rect = pygame.Rect(self.x + self.tank_width / 2, self.y - 5, self.width, self.height)
        # self.bullet = pygame.draw.circle(self.screen, self.color, (self.rect.x, self.rect.y), self.radius)

        self.side_bullet = "up"
        # self.bullet = pygame.transform.scale(image, (self.rect.width, self.rect.height))

    def shooting(self):
        pass

    # def rotate(self, side):
    # self.bullet = pygame.transform.rotate(self.bullet, side)
    def update(self):
        directions = {
            "right": (self.speed, 0),
            "left": (-self.speed, 0),
            "up": (0, -self.speed),
            "down": (0, self.speed)
        }
        if (self.rect.x > BG_SIZE[0] or self.rect.x < 0) or (self.rect.y < 0 or self.rect.y > BG_SIZE[1]):
            Bullet.bullets.remove(self)
        self.rect.x += directions[self.side_tank][0]
        self.rect.y += directions[self.side_tank][1]
        objects = Tank.tanks+Block.blocks
        for object in objects:
            if object.type == "tank" and object.rect.colliderect(self.rect):
                Tank.tanks.remove(object)
                objects.remove(object)
                Bullet.bullets.remove(self)
            if object.type == "wall" and object.rect.colliderect(self.rect):
                Bullet.bullets.remove(self)

            if object.type == "capture_zone" and self.rect.colliderect(object.rect):
                object.collide()
                #object.point_up(self.tank)
                """self.tank.point += 1
                self.tank.point_obj.score = self.tank.point
                for text in texts:
                    if text.name == self.tank.point_name:
                        text.update_text(f"очки {self.tank.point_name}: {self.tank.point}")"""




    def spawn(self, side):
        # self.bullet =
        cords = {
            "right": (self.x + self.tank_width + 5, self.y + self.tank_height / 2),
            "left": (self.x - 5, self.y + self.tank_height / 2),
            "up": (self.x + self.tank_width / 2, self.y - 5),
            "down": (self.x + self.tank_width / 2, self.y + self.tank_height + 5)
        }

        self.rect.x = cords[side][0]
        self.rect.y = cords[side][1]
        # self.bullet = pygame.draw.circle(self.screen, self.color, (self.rect.x, self.rect.y), self.radius)
        self.side_bullet = side
        # self.screen.blit(self.bullet, self.rect)

    def draw(self):
        self.bullet = pygame.draw.circle(self.screen, self.color, (self.rect.x, self.rect.y), self.radius)