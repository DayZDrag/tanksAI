from icecream import ic

from grid_sensor import GridSensor
from image_loader import image_loader

import sys
from random import choice
import pygame
from block import Block, CaptureZone, Wall
from bullet import Bullet

from config_game import bg_color, target_fps, BG_SIZE
from config_neural_loader import config_neural
from lidar import Lidar
from tank import Tank
from text import Text
from tools import filter_tanks_name

#os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
#config = Config()
#print("config = Config() game")
#image_loader = ImageLoader()
tanks_images = image_loader.load_tank_images()
screen = pygame.display.set_mode(BG_SIZE)
clock = pygame.time.Clock()
ic.configureOutput(prefix='DEBUG | ', includeContext=True)

def game():

    tank_1 = Tank(screen, "player", (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE), size=2,
    image=choice(tanks_images))
    #tank_2 = Tank(screen, "2", (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_m), size=6,
    #image=choice(tanks_images))
    #zone = CaptureZone(screen, cords=(BG_SIZE[0]*0.5, BG_SIZE[1]*0.1))
    for _ in range(1):
        CaptureZone(screen, cords=(BG_SIZE[0] * 0.5, BG_SIZE[1] * 0.1))

    grid = GridSensor(screen, (0, 0), 1200, 800, 100, tank_1)


    #Point(name="player", text="очки player", cords=(bg_size[0]*0, bg_size[1]*0))
    #Point(name="neiro", text="очки neiro", cords=(bg_size[0]*0, bg_size[1]*0.05))
    #Text(screen, cords=(bg_size[0]*0, bg_size[1]*0), name="player", text="очки player: 0", size=50)
    #Text(screen, cords=(bg_size[0]*0, bg_size[1]*0.05), name="neiro", text="очки neiro: 0", size=50)
    # TankNeiro()
    local_timer_sec = 0

    for _ in range(10):
        Wall(screen, (0, 0)).update()

    while True:
        ticks = pygame.time.get_ticks()
        global_timer_sec = ticks // 1000

        #print(tank_1.bullet)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(bg_color)



        for bullet in Bullet.bullets:
            bullet.update()
            bullet.draw()




        keys = pygame.key.get_pressed()
        #print(keys)
        #print(pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_m)

        if keys[pygame.K_c] and (filter_tanks_name("player", Tank.tanks) or not Tank.tanks):
           Tank(screen, "player", (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE), size=6, image=choice(tanks_images), cords=(0, 0))

        if keys[pygame.K_x] and (filter_tanks_name("neiro", Tank.tanks) or not Tank.tanks):
            Tank(screen, "neiro", (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_m), size=6,
                     image=choice(tanks_images), cords=(6*16, 0)
                     )

        #old_distance = tank_1.compute_distance(zone)
        #print([tank_1.side_obj, tank_1.distance])





        #new_distance = tank_1.compute_distance(zone)
        #obsalut_d = old_distance - new_distance
        #print(f"{obsalut_d=}")

            #print(f"side obj: {tank.side_obj}\n"
            #      f"distance: {tank.distance}"
            #      )
            #print(pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE)



        for text in Text.texts:
            text.draw()

        for block in Block.blocks:
            block.draw()

        lidar: Lidar
        lidar_list_points = []
        #ic("============")
        ic("=========================")
        for lidar in Lidar.list_lidars:
            lidar.update()
            lidar.draw()
            size_lidar = lidar.size / lidar.distance

            #ic(size_lidar)
            ic(lidar.type_collide_obj)
        ic("=========================")



            # ic(pygame.Vector2(lidar.end_pos))

            #lidar_list_points.append(min(1, point.x))
            #lidar_list_points.append(min(1, point.y))
        #ic(lidar_list_points)

        for tank in Tank.tanks:
            if not tank.is_alive:
                continue
            tank.update(keys)
            tank.draw()

        #ic("=========================")
        #grid.draw()
        #grid.update()


        # ic(grid.cells_list)
        #ic(grid.get_cells_state())
        # ic(grid.cells_list)

        #ic("=========================")



        if local_timer_sec != global_timer_sec:
            local_timer_sec = global_timer_sec
            real_time_fps = clock.get_fps()
            ic(real_time_fps)
            #print(local_timer_sec)

            '''timer_T.update_text(f"таймер: {timer_alive}")
            timer_alive -= 1
            timer_reward -= 1'''

        pygame.display.flip()

        clock.tick(target_fps)

if __name__ == "__main__":
    game()