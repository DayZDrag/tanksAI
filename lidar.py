import math

import pygame

from block import Wall, CaptureZone
from config_game import GREEN_COLOR, DARKENED_GREEN_COLOR, RED_COLOR, BG_SIZE, bg_rect
from config_neural_loader import config_neural


class Lidar:
    list_lidars = []
    def __init__(self, screen, obj, distance, angle):
        Lidar.list_lidars.append(self)
        #ic("create lidar...")

        self.screen = screen
        self.distance = distance
        #self.start_pos = start_pos
        #self.end_pos = end_pos
        self.angle = angle
        self.flag_rotate = config_neural.LIDAR.rotate

        self.type_collide_obj = 0



        self.flag_collide_obj = False



        from tank import Tank
        self.obj: Tank = obj





        #self.line = (start_pos, end_pos)

        self.lidar_sides = {
            "right": pygame.math.Vector2(1, 0),
            "left": pygame.math.Vector2(-1, 0),
            "up": pygame.math.Vector2(0, -1),
            "down": pygame.math.Vector2(0, 1)
        }

        self.to_rotate()

        self.start_pos = pygame.math.Vector2(self.obj.rect.center)
        self.end_pos = self.side_moment * self.distance + pygame.math.Vector2(self.obj.rect.center)

        self.size = round(self.start_pos.distance_to(self.end_pos), 6)

        # pygame.draw.line(self.screen, (0, 100, 0), (x1, y1), (x2, y2), 3)
        # print(distance)


        # line = (self.rect.center, )
        # ic(self.rect.center)

        '''radians = math.radians(self.sides[self.side])
        x = math.sin(radians)
        y = -math.cos(radians)
        (x, y)'''
        # pygame.math.Vector2(self.rect.center)

        # pygame.draw.line(self.screen, GREEN_COLOR, self.rect.center, (side_moment.x*distance+self.rect.center[0]*0**abs(side_moment.x), side_moment.y*distance+self.rect.center[1]*0**abs(side_moment.y)))
        #self.generate_lidars(2, 90, zercal=False)
    def to_rotate(self):
        self.side_moment = self.lidar_sides[self.obj.side]
        self.side_moment = self.side_moment.rotate(self.angle)

    def intersect(self, p1, p2, p3, p4):
        p1 = pygame.math.Vector2(p1)
        p2 = pygame.math.Vector2(p2)
        p3 = pygame.math.Vector2(p3)
        p4 = pygame.math.Vector2(p4)

        r = p2 - p1
        s = p4 - p3
        rxs = r.cross(s)
        q_p = p3 - p1
        q_pxr = q_p.cross(r)

        if rxs == 0:
            return None  # Параллельны или совпадают

        t = q_p.cross(s) / rxs
        u = q_pxr / rxs

        # Для бесконечных прямых:
        # return p1 + r * t

        # Для отрезков:
        if 0 <= t <= 1 and 0 <= u <= 1:
            return p1 + r * t
        else:
            return None



    def update(self):
        if self.flag_rotate:
            self.to_rotate()
        self.start_pos = pygame.math.Vector2(self.obj.rect.center)
        self.end_pos = self.side_moment * self.distance + pygame.math.Vector2(self.obj.rect.center)
        self.flag_collide_obj = False
        self.flag_collide_bg = False
        from block import Block
        from bullet import Bullet

        clip_obj_points = []







        for obj in Block.blocks+Bullet.bullets:
            clip_obj = obj.rect.clipline(self.obj.rect.center, self.end_pos)



            if clip_obj:
                self.flag_collide_obj = True
                clip_obj_points.append((obj, clip_obj[0]))
                clip_obj_points.append((obj, clip_obj[1]))






        if self.flag_collide_obj:
            #self.flag_collide = True
            #self.clamp_point_manual(block.rect, )
            #pygame.draw.line(self.screen, RED_COLOR, *clip_block)
            objects, points = zip(*clip_obj_points)



            self.end_pos = pygame.math.Vector2(min(points, key=lambda p: math.dist(p, self.obj.rect.center)))

            if isinstance(objects[points.index(self.end_pos)], Wall):
                self.type_collide_obj = 0.6
            elif isinstance(objects[points.index(self.end_pos)], CaptureZone):
                self.type_collide_obj = 1



        else:
            if not bg_rect.collidepoint(self.end_pos):
                clip_bg = bg_rect.clipline(self.obj.rect.center, self.end_pos)
                self.end_pos = pygame.math.Vector2(clip_bg[1])
                self.type_collide_obj = 0.3
            else:
                self.end_pos = self.side_moment * self.distance + pygame.math.Vector2(self.obj.rect.center)
                self.type_collide_obj = 0

        self.size = self.start_pos.distance_to(self.end_pos)
            #self.flag_collide = False
        #ic(self.end_pos)



    def draw(self):
        pygame.draw.line(self.screen, GREEN_COLOR, self.start_pos, self.end_pos, width=2)


def generate_lidars(screen, obj, level, distance, start_angle, mirrored=False):
    Lidar(screen, obj, distance, 0)
    for l in range(level):
        l += 1
        Lidar(screen, obj, distance, start_angle/level*l)
        Lidar(screen, obj, distance, -start_angle/level*l)


    if mirrored:
        Lidar(screen, obj, distance, -180)
        for l in range(level):
            l += 1

            if abs(start_angle) == 90 and l == level:
                continue

            Lidar(screen, obj, distance, 180 + start_angle/level*l)
            Lidar(screen, obj, distance, 180 - start_angle/level*l)