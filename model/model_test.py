import sys
from random import choice

import neat_agent
import pygame
import os

import tanksAI.main
from tanksAI.config.config import Config
from tanksAI.main import CaptureZone, bg_size, tanks_images, screen, Tank, bg_color, \
    clock, target_fps

config = Config()

bg = pygame.image.load(os.path.join(config.images_dir, "fon.png")).convert()
bg = pygame.transform.scale(bg, bg_size)
tanks = tanksAI.main.tanks
bullets = tanksAI.main.bullets
blocks = tanksAI.main.blocks
texts = tanksAI.main.texts
def main(genomes, config):
    global tanks

    print("new population")

    #global objects

    #tank_1 = Tank(screen, "1", (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE), size=6,
                  #image=choice(tanks_images))
    #tank_2 = Tank(screen, "2", (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_m), size=6,
                  #image=choice(tanks_images))
    CaptureZone(screen, cords=(bg_size[0]*0.4, bg_size[1]*0.4))
    #Point(name="player", text="очки player", cords=(bg_size[0]*0, bg_size[1]*0))
    #Point(name="neiro", text="очки neiro", cords=(bg_size[0]*0, bg_size[1]*0.05))
    #Text(screen, cords=(bg_size[0]*0, bg_size[1]*0), name="player", text="очки player: 0", size=50)
    #Text(screen, cords=(bg_size[0]*0, bg_size[1]*0.05), name="neiro", text="очки neiro: 0", size=50)
    # TankNeiro()

    filter_tanks_name = lambda name: not [True for tank in tanks if tank.name == name]
    filter_tanks_alive = lambda tanks: [True for tank in tanks if tank.is_alive]

    nets = []

    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        Tank(screen, str(i), (0, 1, 2, 3, 4), size=6,
            image=choice(tanks_images), cords=(bg_size[0]*0.5, bg_size[1]*0.5)
            )

    tanks = tanksAI.main.tanks



    while True:


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        #print(f"tanks: {tanks}")
        #print(f"filter_tanks_alive: {filter_tanks_alive(tanks)}")
        if not filter_tanks_alive(tanks):

            break


        for i, tank in enumerate(tanks, start=0):
            #print(f"i: {i}\nlen nets: {nets}\nlen tanks: {len(tanks)}")
            if not tank.is_alive:
                continue
            data_list = []
            data = tank.get_data()

            data_list.append(data)
            #print(data)
            output = nets[i].activate(data_list)
            keys = [0]*5
            #keys = output + [0]
            keys[output.index(max(output))] = 1

            #print(keys)
            print(f"info: \ntank: {tank.name}\ninput: {data}\noutput: {keys}\nrealy output: {output}")


            """for side in output:
                if side > 0.5:
                    keys.append(1)
                else:
                    keys.append(0)
            keys.append(0)"""
            #print(keys)
            tank.update(keys)


            '''if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                pygame.quit()
                sys.exit()'''
        #keys = pygame.key.get_pressed()
        #print(bullets)

        #x = map(filter_tanks_name, tanks)
        #name
            #filter_tanks_name = lambda tank, name:


        #print(filter_tanks_name("player"))

        '''if keys[pygame.K_c] and (filter_tanks_name("player") or not tanks): #(all([True for tank in tanks if ])
            Tank(screen, "player", (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE), size=6,
                     image=choice(tanks_images), cords=(0, 0)
                     )

        if keys[pygame.K_x] and (filter_tanks_name("neiro") or not tanks):
            Tank(screen, "neiro", (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_m), size=6,
                     image=choice(tanks_images), cords=(6*16, 0)
                     )'''
        # if keys[pygame.K_x]:
        #    tanks.append(tank_1)

        #print(len(tanks))


        # keys[event.key]()
        # print(event.key)

        # tank = create_tank()
        # tank_rect = tank.get_rect()
        # tank_rect_x_y = (tank_rect.x, tank_rect.y)
        # tank_rect.move_ip(tank_rect_x_y[0]+1, tank_rect_x_y[1])
        # x = tank_rect_x_y[0] + 1
        # y = tank_rect_x_y[1]
        # screen.blit(tank, tank_rect)
        # print(x)

        #
        # print(len(bullets))
        #objects=tanks+blocks
        #keys = [False, False, False, False, False]


        for bullet in bullets:
            bullet.update()
            bullet.draw()


        """for object in objects:
            if object.type == "tank":
                object.update(keys)
            object.draw()"""

        screen.fill(bg_color)
        screen.blit(bg, (0, 0))

        for i, tank in enumerate(tanks):
            if not tank.is_alive:
                continue

            tank.draw()
            genomes[i][1].fitness += tank.get_data() / 100
            if tank.reward:
                genomes[i][1].fitness += 10
                tank.reward = False


        for block in blocks:
            block.draw()

        for text in texts:
            text.draw()


        #print(tanks)

        #objects=tanks+blocks




        # pygame.draw.rect(screen, (255,255,255), (10,10,10,10))

        pygame.display.flip()

        clock.tick(target_fps)

    tanks = []
    tanksAI.main.tanks = []




if __name__ == "__main__":
    #print(config.model_dir)
    config_path = config.model_dir+"\\config-feedforward.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Create core evolution algorithm class
    p = neat.Population(config)

    # Add reporter for fancy statistical result
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run NEAT
    p.run(main, 1000)
