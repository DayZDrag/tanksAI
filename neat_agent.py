import sys
from random import randint, choice

import neat
import pygame

from block import Block, CaptureZone
from bullet import Bullet
from config.config import Config
from config_game import screen, BG_SIZE, TIME_FIT, bg_color, clock, target_fps
from tank import Tank, tanks_images
from text import Text
from tools import filter_tanks_alive

pygame.init()
config = Config()


CONST_TA = 10
timer_alive = CONST_TA
text_timer = f"таймер: {CONST_TA}"
generation = 1
text_generation = f"поколение: {generation}"
text_tanks = f"танки: 50"



Text(screen, cords=(BG_SIZE[0]/2.2, BG_SIZE[1] * 0.05), name="timer", text=text_timer, size=50)
Text(screen, cords=(BG_SIZE[0]*0.05, BG_SIZE[1] * 0.05), name="generation", text=text_generation, size=50)
Text(screen, cords=(BG_SIZE[0]*0.8, BG_SIZE[1] * 0.05), name="tanks", text=text_tanks, size=50)

#for _ in range(10):
CaptureZone(screen, cords=(BG_SIZE[0]*0.5, BG_SIZE[1]*0.1))





def main(genomes, config):
    global timer_alive, generation

    #flag_stop_game = False
    for block in Block.blocks:
        if block.type == "capture_zone":
            block.rect.x = randint(0, BG_SIZE[0]-block.width)
            block.rect.y = randint(0, BG_SIZE[1]-block.height)


    print("new population")



    nets = []


    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        Tank(screen, str(i), (0, 1, 2, 3, 4), size=6,
            image=choice(tanks_images), cords=(BG_SIZE[0]*0.5, BG_SIZE[1]*0.5)
            )



    local_timer_sec = 0
    flag_stop_game = False
    while True:

        ticks = pygame.time.get_ticks()
        global_timer_sec = ticks//1000

        '''if local_timer_sec != global_timer_sec:
            local_timer_sec = global_timer_sec'''



        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        #print(f"tanks: {tanks}")
        #print(f"filter_tanks_alive: {filter_tanks_alive(tanks)}")
        if not filter_tanks_alive(Tank.tanks):

            break


        for i, tank in enumerate(Tank.tanks, start=0):
            #print(f"i: {i}\nlen nets: {nets}\nlen tanks: {len(tanks)}")
            if not tank.is_alive:
                continue

            #data_list = []
            data = []
            for block in Block.blocks:
                if block.type == "capture_zone":
                    data = tank.get_data(block)
                    break

            #data_list.append(data)
            #print(data)
            output = nets[i].activate(data)
            keys = [0]*5
            #keys = output + [0]
            #keys[-1] = random()
            keys[output.index(max(output))] = 1

            #print(keys)
            tank_fitness_info = genomes[i][1].fitness
            '''print(f"info: \n"
                  f"tank: {tank.name}\n"
                  f"input: {data}\n"
                  f"output: {keys}\n"
                  f"realy output: {output}\n"
                  f"fitness: {tank_fitness_info}\n"
                  f"side obj: {tank.side_obj}")'''



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


        for bullet in Bullet.bullets:
            bullet.update()
            bullet.draw()


        """for object in objects:
            if object.type == "tank":
                object.update(keys)
            object.draw()"""

        screen.fill(bg_color)
        #screen.blit(bg, (0, 0))

        for i, tank in enumerate(Tank.tanks):
            if not tank.is_alive:
                continue
            tank.draw()
            for text in Text.texts:
                if text.name == "tanks":
                    text.update_text(f"танки: {sum(filter_tanks_alive(Tank.tanks))}/{len(Tank.tanks)}")
            #genomes[i][1].fitness += tank.get_data()

            genomes[i][1].fitness += tank.reward
            tank.reward = 0


        for block in Block.blocks:
            block.draw()

        #print(f"global_timer_sec: {global_timer_sec}")
        #print(f"local_timer_sec: {local_timer_sec}")

        for text in Text.texts:
            text.draw()
            if text.name == "timer":
                if local_timer_sec != global_timer_sec:
                    #print("update time")
                    #timer_alive = 0
                    timer_alive -= 1
                    '''if tank.time_alive_tank < 0:
                        tank.is_alive = False'''
                    if timer_alive < 0:
                        flag_stop_game = True

                    '''if timer_alive < tank.time_alive_tank:
                        timer_alive = tank.time_alive_tank'''

                    local_timer_sec = global_timer_sec

                    for tank in Tank.tanks:
                        tank.reward += TIME_FIT





                    text.update_text(f"таймер: {timer_alive}")

        #print(f"flag_stop_game: {flag_stop_game}")
        #print(f"timer_alive: {timer_alive}")


        #global_timer_sec
        if flag_stop_game:
            break




        #print(tanks)

        #objects=tanks+blocks




        # pygame.draw.rect(screen, (255,255,255), (10,10,10,10))

        pygame.display.flip()

        clock.tick(target_fps)
    flag_stop_game = False
    timer_alive = CONST_TA

    Tank.tanks = []
    generation += 1
    for text in Text.texts:
        if text.name == "generation":
            text.update_text(f"поколение: {generation}")





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
    #game()
    p.run(main, 10000)
