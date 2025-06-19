import os
import sys
from pprint import pprint

import pygame
import torch
import random
#import numpy as np
from collections import deque

from sympy.codegen import Print

from block import CaptureZone
from bullet import Bullet
from config_game import bg_color, BG_SIZE, target_fps, ORANGE_COLOR, GREEN_COLOR, RED_COLOR, TIME_FIT  # screen, clock
from image_loader import image_loader
from model_q_torch import QNetworkTorch, QTrainer
#from plot import plot
#import plot
from tank import Tank
from text import Text, Point
#import os
import torch.nn.functional as F

from tools import ocurat_print

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

#print("загрузка...")

#использование только 1 процесса
#torch.set_num_threads(1)

class Agent:

    def __init__(self, model):


        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = model
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

        self.flag_training = True

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory
        print(f"{mini_sample=}")

        try:
            states, actions, rewards, next_states, dones = zip(*mini_sample)
            self.trainer.train_step(states, actions, rewards, next_states, dones)
        except:
            print("ни одного попадания")


    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)


    def get_action(self, state):
        K_len_learn = 0.01
        self.epsilon = 80*K_len_learn - self.n_games
        final_move = [0]*5
        if random.randint(0, 200*K_len_learn) < self.epsilon:
            move = random.randint(0, 3)
            final_move[move] = 1

        else:
            state0 = torch.tensor(state, dtype=torch.float)
            #print(state0)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

    def get_action_lite_random(self, state):
        final_move = [0] * 5

        if random.randint(1, 10) == self.flag_training:#self.flag_rand_stachiochastic#1
            move = random.randint(0, 3)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
            #print(final_move)

        return final_move
    def get_action_stahiohastic(self, state):
        final_move = [0] * self.model.fc3.out_features

        temperature = 1

        #print("=======================")
        #print(f"object: {self.__class__.__name__}")
        state0 = torch.tensor(state, dtype=torch.float)
        #print(f"{state=}")
        prediction = self.model(state0)
        #print(f"{prediction=}")
        probs = F.softmax(prediction / temperature, dim=0)
        #print(f"{probs=}")
        move = torch.multinomial(probs, num_samples=1).item()
        #print(f"{move=}")
        final_move[move] = 1
        #print(probs)
        #print("=======================")

        return final_move


def train():
    pygame.init()
    screen = pygame.display.set_mode(BG_SIZE)
    clock = pygame.time.Clock()

    plot_scores = []
    plot_mean_scores = []
    total_score = 0

    done = False


    agent_tank = Agent(QNetworkTorch(1, 100, 100,  4))
    #agent_gun = Agent(QNetworkTorch(4, 100, 100,  2))
    reward_gun = 0

    tank = Tank(screen, "neiro", (0, 1, 2, 3, 4), size=6,
            image=image_loader.tanks_images[1], cords=(BG_SIZE[0]*0.5, BG_SIZE[1]*0.5)
                )

    zone = CaptureZone(screen, cords=(BG_SIZE[0]*0.5, BG_SIZE[1]*0.1))

    local_timer_sec = 0
    time_game = 0

    min_distance = 1000
    max_distance = 0

    CONST_TA = 5
    CONST_TR = CONST_TA
    timer_reward = CONST_TR
    timer_alive = CONST_TA
    text_timer = f"таймер: {timer_alive}"

    #texts
    timer_T = Text(screen, cords=(BG_SIZE[0] * 0.8, BG_SIZE[1] * 0.05), name="timer", text=text_timer, size=50)

    agent_tank.n_games += 1
    n_game_T = Text(screen, cords=(BG_SIZE[0] * 0.05, BG_SIZE[1] * 0.05), name="n_game", text=f"раунд: {agent_tank.n_games}", size=50)

    score_T = Text(screen, cords=(BG_SIZE[0]*0.45, BG_SIZE[1] * 0.05), name="score", text=f"счёт: {tank.score}", size=50)


    record_tank = 0
    record_T = Text(screen, cords=(BG_SIZE[0] * 0.8, BG_SIZE[1] * 0.1), name="record", text=f"рекорд: {record_tank}",
                   size=50)
    #rm - random move

    flag_rm_text_T = Text(screen, cords=(BG_SIZE[0] * 0.05, BG_SIZE[1] * 0.1), name="flag_rm_text",
                     text=f"режим:",
                     size=50)

    flag_rm_T = Text(screen, cords=(BG_SIZE[0] * 0.05, BG_SIZE[1] * 0.15), name="flag_rm", text=str(agent_tank.flag_training),
                     size=50)
    flag_rm_T.update_text(text="тренировка", color=GREEN_COLOR) #тренировка/AI

    fps_T = Text(screen, cords=(BG_SIZE[0] * 0.05, BG_SIZE[1] * 0.05), name="fps",
                     text="fps: 0",
                     size=50)

    reward_text_T = Text(screen, cords=(BG_SIZE[0] * 0.8, BG_SIZE[1] * 0.1), name="flag_rm", text="награда:", size=50)

    reward_T = Text(screen, cords=(BG_SIZE[0] * 0.93, BG_SIZE[1] * 0.1), name="flag_rm", text="0", size=50)

    '''sum_reward_move = Text(screen, cords=(BG_SIZE[0] * 0.93, BG_SIZE[1] * 0.1), name="sum_reward_move", text="0", size=50)
    sum_reward_move_T = Text(screen, cords=(BG_SIZE[0] * 0.93, BG_SIZE[1] * 0.1), name="sum_reward_move", text="0", size=50)
    sum_reward_move = Point(screen, name=)
    
    sum_reward_gun
    sum_reward_gun_T'''


    #bufer_train_bullet_memory = []
    bufer_train_bullet = []
    flag_train_long_memory = True
    start = True
    sum_reward_move = 0
    sum_reward_gun = 0
    count_gun = 0
    count_move = 0
    while True:


        ticks = pygame.time.get_ticks()
        global_timer_sec = ticks // 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    start = True

                if event.key == pygame.K_x and agent_tank.flag_training: # and False
                    agent_tank.flag_training = False
                    flag_rm_T.update_text(text="Эксплуатация", color=RED_COLOR)
                elif event.key == pygame.K_x and not agent_tank.flag_training:
                    agent_tank.flag_training = True
                    flag_rm_T.update_text(text="тренировка", color=GREEN_COLOR)
                elif event.key == pygame.K_s:
                    agent_tank.model.save() #f"{local_timer_sec}"
                elif event.key == pygame.K_l:
                    model = QNetworkTorch(4, 10, 4)
                    model.load_state_dict(torch.load(os.path.join("saves", 'model.pth')))
                    #model.eval()
                    agent_tank = Agent(model)
                    time_game = 0
                    tank.score = 0
                    tank.rect.x = BG_SIZE[0]*0.5
                    tank.rect.y = BG_SIZE[1]*0.5
                    agent_tank.flag_training = False
                    timer_T.update_text(f"время: {time_game}")
                    flag_rm_T.update_text(text="Эксплуатация", color=RED_COLOR)
                    score_T.update_text(f"счёт: {tank.score}")
                elif event.key == pygame.K_r:
                    agent_tank = Agent()
                    time_game = 0
                    tank.score = 0
                    tank.rect.x = BG_SIZE[0] * 0.5
                    tank.rect.y = BG_SIZE[1] * 0.5
                    agent_tank.flag_training = True
                    timer_T.update_text(f"время: {time_game}")
                    flag_rm_T.update_text(text="тренировка", color=GREEN_COLOR)
                    score_T.update_text(f"счёт: {tank.score}")
        if not start:
            continue





        '''keys_user = pygame.key.get_pressed()
        if keys_user[pygame.K_x] and agent_tank.flag_rand_stachiochastic:
            agent_tank.flag_rand_stachiochastic = False
            flag_rm_T.update_text(text=str(agent_tank.flag_rand_stachiochastic), color=RED_COLOR)
        elif keys_user[pygame.K_x] and not agent_tank.flag_rand_stachiochastic:
            agent_tank.flag_rand_stachiochastic = True
            flag_rm_T.update_text(text=str(agent_tank.flag_rand_stachiochastic), color=GREEN_COLOR)'''

        screen.fill(bg_color)

        for bullet in Bullet.bullets:
            bullet.update()
            bullet.draw()

        state_old = tank.get_data(zone)
        #print(state_old)
        #print(state_old)
        #print(tank.bullet)

        old_distance = tank.compute_distance(zone)
        #print(state_old)
        #print("state_old[0:4]", state_old[0:4])


        #keys = agent_tank.get_action(state_old)
        #@ocurat_print()
        keys_tank = agent_tank.get_action_stahiohastic(state_old[0:1])
        #keys_gun = agent_gun.get_action_stahiohastic(state_old)
        #print(f"{keys_tank=}")
        #print(f"{keys_gun=}")
        keys_tank.append(0)
        keys = keys_tank


        #keys.append(keys_gun[1])
        #print(f"{keys=}")
        #print(f"{keys_gun=}")
        #print(f"{keys=}")



        #tank.update(keys)
        tank.update(keys_tank)
        #keys.pop()
        #print(f"reward_tank: {tank.reward_tank}")
        reward_tank = tank.reward
        #print(reward_tank)
        #no_revers_reward = local_timer_sec-CONST_TA
        if tank.flag_timer_reward:
            tank.flag_timer_reward = False
            timer_reward = CONST_TR
            timer_alive = CONST_TA





        no_revers_reward = timer_reward-CONST_TA
        #print(f"{timer_reward=}")

        new_distance = tank.compute_distance(zone)
        difference_distance = old_distance-new_distance

        '''if new_distance < min_distance:
            min_distance = new_distance
            reward_tank += 10'''

        '''if new_distance > min_distance:
            reward_tank -= 0.1'''
        '''if 2 > difference_distance > 0:
            difference_distance = 0'''
        '''if difference_distance > 0:
            reward_tank+=10'''
        '''elif difference_distance < 0:
            reward_tank -= 1'''
        reward_tank += max(-0.1, difference_distance)
        count_move += 1
        sum_reward_move += reward_tank
        #reward_tank += min(0.1, difference_distance)
        #reward_tank = reward_tank/1.5
        #reward_tank += no_revers_reward
        #print(f"{reward_tank=}")
        #points_in_second = tank.score / global_timer_sec
        #print(f"{points_in_second=}")


        #print(f"{tank.compute_distance(zone)}")
        if reward_tank > 0:
            reward_T.update_text(f"{reward_tank:.1f}", color=GREEN_COLOR)
        elif reward_tank < 0:
            reward_T.update_text(f"{reward_tank:.1f}", color=RED_COLOR)
        else:
            reward_T.update_text(f"{reward_tank:.1f}", color=RED_COLOR)
        #print(f"{no_revers_reward=}")
        #print(f"{difference_distance=}")
        #print(f"{min_distance=}")




        score_T.update_text(f"счёт: {tank.score}")

        '''if agent_tank.flag_learning_ai == "рандом":
            flag_rm_T.update_text(text=agent_tank.flag_learning_ai, color=RED_COLOR)

        elif agent_tank.flag_learning_ai == "Эксплуатация":
            flag_rm_T.update_text(text=agent_tank.flag_learning_ai, color=GREEN_COLOR)'''



        if not tank.is_alive:
            done = True
            tank.is_alive = True

        # perform move and get new state
        #reward_tank, done = game.play_step(final_move)
        #print(frame_iteration)


        state_new = tank.get_data(zone)

        #state_new.pop()
        #print(f"{state_new=}")

        #print(f"len: {len(bufer_train_bullet)}")

        '''if agent_tank.flag_training:
            tank.score -= 1'''






        if agent_tank.flag_training:
            state_new_gun = state_old[0:1]
            state_new_gun.extend(state_new[1:])
            reward_gun = 0
            if not state_old[-2]:
                reward_gun = 0.01

            #print(f"{state_old=}")
            #print(f"{state_new=}")
            #print(f"{state_new_gun=}")



            if keys[4]:


                #reward_tank = 0
                if state_old[-2]:
                    reward_gun = -10
                    #print(f"{state_old=}")
                    #print(f"{reward_gun}")
                else:
                    reward_gun = -5
                    #print(reward_gun)

                sum_reward_gun += reward_gun
                state_new[-1] = 1
                state_new_gun = state_old[0:1]
                state_new_gun.extend(state_new[1:])
                #print(f"{state_old=}")
                #print(f"{state_new_gun=}")

                bufer_train_bullet.append(
                    ([state_old, keys_gun, 100, state_new_gun, done], tank.bullet) #max(1, min(1200, tank.compute_distance(zone) - 600+600)/2)
                                          )
                #print(state_old, keys, reward_tank, state_new, done)
            # тренировка короткой памяти
            #print(state_new_gun)
            agent_tank.train_short_memory(state_old[0:1], keys_tank, reward_tank, state_new[0:1], done)
            #agent_gun.train_short_memory(state_old, keys_gun, reward_gun, state_new_gun, done)

        #print(reward_tank)

        #print(f"len={len(bufer_train_bullet)}")
        if tank.flag_collide_bullet_zone:
            tank.flag_collide_bullet_zone = False
            for state_bullet in bufer_train_bullet:
                if state_bullet[1] is tank.bullet:
                    #state_bullet[0][2] = tank.reward_tank
                    state_old, keys_gun, reward_gun, state_new, done = state_bullet[0]
                    #agent_gun.train_short_memory(state_old, keys_gun, reward_tank, state_new, done)
                    #agent_gun.remember(state_old, keys_gun, reward_gun, state_new, done)
                    #print(f"reward_gun bullet distance: {reward_gun}")
                    sum_reward_gun += reward_gun
                    count_gun += 1
                    #bufer_train_bullet_memory.append(state_bullet[0])
                    #print(f"tank.bullet {tank.bullet}")
                    #print(state_bullet)
                    #print("======================")
                    #print(f"{state_old=}")
                    #print(f"{state_new=}")
                    #print(f"{keys_gun=}")
                    #print(f"{keys=}")
                    #print(f"{reward_gun=}")
                    #print("======================")
                    break
            bufer_train_bullet = []

        if time_game % 2 == 0 and time_game and flag_train_long_memory and False:
            #agent_gun.train_long_memory()
            flag_train_long_memory = False
            print(f"{count_move=}")
            print(f"{count_gun=}")

        #print(f"{sum_reward_move=}")
        #print(f"{sum_reward_gun=}")









        if local_timer_sec != global_timer_sec:
            local_timer_sec = global_timer_sec
            time_game += 1

            #timer_T.update_text(f"таймер: {timer_alive}")
            #timer_alive -= 1
            timer_T.update_text(f"время: {time_game}")
            timer_reward -= TIME_FIT
            flag_train_long_memory = True


            #print(local_timer_sec)

        if timer_alive < 0:
            #done = True
            pass


        tank.draw()
        zone.draw()

        timer_T.draw()
        #n_game_T.draw()
        score_T.draw()
        #record_T.draw()
        flag_rm_text_T.draw()
        flag_rm_T.draw()
        reward_T.draw()
        reward_text_T.draw()
        fps_T.draw()

        tank.reward = 0

        pygame.display.flip()
        #clock.tick(target_fps)

        #tank.score = 0
        if not agent_tank.flag_training:
            clock.tick(target_fps)
        else:
            clock.tick()
        real_time_fps = clock.get_fps()
        fps_T.update_text(f"fps: {real_time_fps:.1f}")
        # clock.tick(300)
        # clock.tick()
        #print(f"{real_time_fps=}")

        if done:
            # train long memory, plot result
            #game.reset()
            zone.collide()# = CaptureZone(screen, cords=(BG_SIZE[0] * 0.5, BG_SIZE[1] * 0.1))

            tank.rect.x = BG_SIZE[0] * 0.5
            tank.rect.y = BG_SIZE[1] * 0.5


            #frame_iteration = 0
            timer_reward = CONST_TR
            agent_tank.n_games += 1
            min_distance = 1200
            max_distance = 0
            #print(agent_tank.n_games)
            #agent_tank.train_long_memory()
            done = False

            timer_alive = CONST_TA
            #timer_T.update_text(f"таймер: {timer_alive}")
            timer_T.update_text(f"время: 0")
            n_game_T.update_text(f"раунд: {agent_tank.n_games}")

            if record_tank < tank.score:
                record_tank = tank.score
                record_T.update_text(f"рекорд: {record_tank}")
                #agent_tank.model.save(f"new_record_{record_tank}")

            '''if agent_tank.n_games % 50 == 0:
                agent_tank.model.save(f"round_{agent_tank.n_games}")'''


            '''if score > record:
                record = score
                agent_tank.model.save()

            print('Game', agent_tank.n_games, 'Score', score, 'Record:', record)'''

            '''plot_scores.append(tank.score)
            total_score += tank.score
            mean_score = total_score / agent_tank.n_games
            plot_mean_scores.append(mean_score)
            plot.plot(plot_scores, plot_mean_scores)'''



if __name__ == '__main__':
    train()