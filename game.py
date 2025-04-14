from image_loader import image_loader

#from image_loader import image_loader
#print("image_loader")
import sys
from random import choice
import pygame
from block import Block, CaptureZone
from bullet import Bullet
#from config.config import Config
from config_game import bg_color, target_fps, BG_SIZE
from tank import Tank
from text import Text
from tools import filter_tanks_name

pygame.init()
#config = Config()
#print("config = Config() game")
#image_loader = ImageLoader()
tanks_images = image_loader.load_tank_images()
screen = pygame.display.set_mode(BG_SIZE)
clock = pygame.time.Clock()

def game():

    tank_1 = Tank(screen, "player", (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE), size=6,
    image=choice(tanks_images))
    #tank_2 = Tank(screen, "2", (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_m), size=6,
    #image=choice(tanks_images))
    zone = CaptureZone(screen, cords=(BG_SIZE[0]*0.5, BG_SIZE[1]*0.1))

    #Point(name="player", text="очки player", cords=(bg_size[0]*0, bg_size[1]*0))
    #Point(name="neiro", text="очки neiro", cords=(bg_size[0]*0, bg_size[1]*0.05))
    #Text(screen, cords=(bg_size[0]*0, bg_size[1]*0), name="player", text="очки player: 0", size=50)
    #Text(screen, cords=(bg_size[0]*0, bg_size[1]*0.05), name="neiro", text="очки neiro: 0", size=50)
    # TankNeiro()

    local_timer_sec = 0

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

        if keys[pygame.K_c] and (filter_tanks_name("player") or not Tank.tanks):
           Tank(screen, "player", (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE), size=6, image=choice(tanks_images), cords=(0, 0))

        if keys[pygame.K_x] and (filter_tanks_name("neiro") or not Tank.tanks):
            Tank(screen, "neiro", (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_m), size=6,
                     image=choice(tanks_images), cords=(6*16, 0)
                     )

        old_distance = tank_1.compute_distance(zone)



        for tank in Tank.tanks:
            if not tank.is_alive:
                continue
            tank.update(keys)
            tank.draw()

        new_distance = tank_1.compute_distance(zone)
        obsalut_d = old_distance - new_distance
        #print(f"{obsalut_d=}")

            #print(f"side obj: {tank.side_obj}\n"
            #      f"distance: {tank.distance}"
            #      )
            #print(pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE)


        for text in Text.texts:
            text.draw()

        for block in Block.blocks:
            block.draw()
            #pass

        if local_timer_sec != global_timer_sec:
            local_timer_sec = global_timer_sec
            print(local_timer_sec)

            '''timer_T.update_text(f"таймер: {timer_alive}")
            timer_alive -= 1
            timer_reward -= 1'''

        pygame.display.flip()

        clock.tick(target_fps)

if __name__ == "__main__":
    game()