import os
import sys
from datetime import datetime
from pprint import pprint

import numpy as np
import pygame
import torch
import random
#import numpy as np
from collections import deque

from PIL.FontFile import WIDTH
from matplotlib import pyplot as plt
from pygame.examples.moveit import HEIGHT
from pyinstrument import Profiler
from sympy.codegen import Print

import config.config
from agent import Agent
from block import CaptureZone, Block, Wall
from bullet import Bullet
from config_experiment_loader import config_experiment

from config_game import bg_color, BG_SIZE, target_fps, ORANGE_COLOR, GREEN_COLOR, RED_COLOR, TIME_FIT, \
    DARKENED_GREEN_COLOR, flag_draw, flag_load_model, MAX_MEMORY, LR, BATCH_SIZE, size_input, \
    size_hidden, size_output, enable_dueling_dqn, experiment, name_load_model, count_zones, \
    flag_experiment_save, model_folder_path, model_saves_path, flag_load_last_model, \
    epsilon_min, epsilon_decay, episode_step, save_model_step, flag_print_fps, flag_debug, DATE_PROJECT, prefix, \
    DATE_FORMAT, flag_train_gun, flag_noise_bias, flag_approach, k_size_reward_approach, min_reward_approach, GUN_FIT
from grid_sensor import GridSensor

from image_loader import image_loader
from lidar import Lidar
from model_q_torch import QNetworkTorch, QTrainer
#from plot import plot
#import plot
from tank import Tank
from text import Text, Point
#import os
import torch.nn.functional as F
from icecream import ic

from tools import ocurat_print, log
from config_neural_loader import config_neural

from config_game import device
import shutil
import json


ic.configureOutput(prefix=f'{prefix} | ', includeContext=flag_debug)

ic(device)




#print("загрузка...")

#использование только 1 процесса
#torch.set_num_threads(1)




def compute_distance_bullet(tank):
    old_distance_bullet = 10000
    for bullet in Bullet.bullets:

        local_dist = tank.compute_distance(bullet)
        if local_dist < old_distance_bullet:
            old_distance_bullet = local_dist

    if not Bullet.bullets:
        old_distance_bullet = -1
        return old_distance_bullet

    return old_distance_bullet/1200


def type_action(agent: Agent, type_act):

    return agent.acts[type_act]

def input_type(tank: Tank, type_input, lidar_list_data=None, capture_zone=None, grid_data =None):
    inputs = {
        config_neural.LIDAR.name: lidar_list_data,
        config_neural.NEAREST_TARGET_VALUE.name: None,
        config_neural.GRID_SENSOR.name: grid_data

    }
    return tank.get_data(data=inputs[type_input], capture_zone=capture_zone)




def load_model(experiment_l, name="model", count_runs=1):

    if flag_load_last_model:
        folder = os.path.join(model_folder_path, experiment_l, model_saves_path, f"run_{count_runs}")
        files = [os.path.join(folder, f) for f in os.listdir(folder) if
                 os.path.isfile(os.path.join(folder, f))]


        # Сортируем по дате создания (или изменения)
        path = max(files, key=os.path.getctime)  # или os.path.getmtime для даты последней модификации
    else:
        folder = os.path.join(model_folder_path, experiment_l, model_saves_path, f"run_{config_experiment.EXPERIMENT.path_run}")
        path = os.path.join(folder, f'{name}.pth')


    print(f"load model: {path}")

    policy_dqn = QNetworkTorch(size_input, size_hidden, size_hidden, size_output,
                               enable_dueling_dqn=enable_dueling_dqn, flag_noise_bias=flag_noise_bias).to(device)

    policy_dqn.load_state_dict(torch.load(path))

    return policy_dqn

def write_log(message):
    with open(os.path.join("saves", experiment, "info.log"), 'a') as file:
        file.write(message + '\n')

def write_info_runs(count_runs, count_steps, count_episodes, record, epsilon):
    data = {
        "count_runs": count_runs,
        "steps": count_steps,
        "episode": count_episodes,
        "record": record,
        "epsilon": epsilon
        }

    with open(os.path.join(model_folder_path, experiment, model_saves_path, "info_runs.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_info_runs():
    path = os.path.join(model_folder_path, experiment, model_saves_path, "info_runs.json")
    if not os.path.isfile(path):
        write_info_runs(0, 0, 0, 0, config_neural.GET_ACTION_EPSILON.epsilon_init)

    with open(path, "r", encoding="utf-8") as f:
        info_runs = json.load(f)
    return info_runs


def write_data_graph(data):
    path = os.path.join(model_folder_path, experiment, "data_graph.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)

def load_data_graph():
    path = os.path.join(model_folder_path, experiment, "data_graph.json")
    if not os.path.isfile(path):
        data = [[], []]
        write_data_graph(data)
        return data


    with open(path, "r", encoding="utf-8") as f:
        data_graph = json.load(f)


    return data_graph

def save_graph(data):
    write_data_graph(data)
    epsilon_history, episodes_score = data

    # Построение графика

    path = os.path.join(model_folder_path, experiment, "graph.png")
    plt.autoscale(True)
    '''plt.plot(episode_records, color="#0069D1")

    # Добавим подписи осей и заголовок (по желанию)
    plt.xlabel('episode')
    plt.ylabel('point')
    plt.title('points of episodes')'''

    #avg = np.mean(episode_records)

    # Создаём одну фигуру с двумя осями
    fig, axs = plt.subplots(3, 1)  # 10x8 дюймов, 2 строки, 1 колонка

    #plt.ylim(bottom=0)
    # 1 график — просто значения
    axs[0].plot(episodes_score, label="очки")
    axs[0].legend()
    axs[0].set_title("очки")
    #axs[0].set_xlim(1, len(episodes_score))

    # 2 график — отклонения от среднего
    mean_values = [sum(episodes_score[:i+1])/i for i in range(1, len(episodes_score))]
    if mean_values:
        mean_value = mean_values[-1]
        ic(mean_value)

    axs[1].plot(mean_values, label="среднее значение")
    axs[1].legend()
    axs[1].set_title("среднее значение")

    axs[2].plot(epsilon_history, label="epsilon")
    axs[2].legend()
    axs[2].set_title("epsilon")

    # Сохранение графика в файл (например, PNG)
    plt.tight_layout()
    plt.savefig(path)
    plt.close('all')
    print("save graph...")

def create_L_1(screen):

    for _ in range(0):
        Wall(screen, (0, 0)).update()


    x_wall = Wall(screen, (320, 0))
    for _ in range(1, 4):
        x_wall = Wall(screen, (x_wall.rect.x, x_wall.rect.y+x_wall.width))

    x_wall = Wall(screen, (128, 192))
    for _ in range(1, 5):
        x_wall = Wall(screen, (x_wall.rect.x + x_wall.height, x_wall.rect.y))


    x_wall = Wall(screen, (BG_SIZE[0] - 384, 0))
    for _ in range(1, 5):
        x_wall = Wall(screen, (x_wall.rect.x, x_wall.rect.y + x_wall.width))

    x_wall = Wall(screen, (BG_SIZE[0]- 192, 192))
    for _ in range(1, 6):
        x_wall = Wall(screen, (x_wall.rect.x - x_wall.height, x_wall.rect.y))





    x_wall = Wall(screen, (320, BG_SIZE[1]-64))
    for _ in range(1, 5):
        x_wall = Wall(screen, (x_wall.rect.x, x_wall.rect.y - x_wall.width))

    x_wall = Wall(screen, (128, BG_SIZE[1]-256))
    for _ in range(1, 6):
        x_wall = Wall(screen, (x_wall.rect.x + x_wall.height, x_wall.rect.y))


    x_wall = Wall(screen, (BG_SIZE[0] - 384, BG_SIZE[1] - 64))
    for _ in range(1, 4):
        x_wall = Wall(screen, (x_wall.rect.x, x_wall.rect.y - x_wall.width))

    x_wall = Wall(screen, (BG_SIZE[0] - 192, BG_SIZE[1] - 256))
    for _ in range(1, 5):
        x_wall = Wall(screen, (x_wall.rect.x - x_wall.height, x_wall.rect.y))


def create_one_wall(screen):
    Wall(screen, (500, 400))

def create_multi_wall(screen):
    Wall(screen, (500, 400))
    Wall(screen, (500, 600))

def train():
    #global device


    if not flag_draw:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    screen = pygame.display.set_mode(BG_SIZE)#, pygame.HIDDEN
    clock = pygame.time.Clock()

    ic(experiment)


    epsilon_history, episodes_score = load_data_graph()


    #plot_mean_scores = []
    #total_score = 0

    count_train_target_steps = 0
    const_train_target_step = config_neural.CONST.train_target_step

    count_action_steps_train = 0
    const_action_step_train = config_neural.CONST.action_step_train

    count_step_train_long_memory = 0
    const_train_long_memory = config_neural.CONST.train_long_memory
    flag_train_long_memory = config_neural.FLAGS.train_long_memory
    flag_train_short_memory = config_neural.FLAGS.train_short_memory





    info_runs = load_info_runs()

    count_runs = info_runs["count_runs"]

    count_steps = info_runs["steps"]
    count_episodes = info_runs["episode"]

    record_tank = info_runs["record"]

    epsilon = info_runs["epsilon"]
    #epsilon_history.append(epsilon)





    done = False

    if flag_load_model:
        policy_dqn = load_model(experiment, name=name_load_model, count_runs=count_runs)
    else:
        policy_dqn = QNetworkTorch(size_input, size_hidden, size_hidden, size_output,
                                   enable_dueling_dqn=enable_dueling_dqn, flag_noise_bias=flag_noise_bias).to(device)



    target_dqn = QNetworkTorch(size_input, size_hidden, size_hidden,  size_output, enable_dueling_dqn=enable_dueling_dqn, flag_noise_bias=flag_noise_bias).to(device)
    target_dqn.load_state_dict(policy_dqn.state_dict())




    agent_tank = Agent(policy_dqn, target_dqn, enable_double_dqn=config_neural.MODEL.enable_double_dqn)
    #agent_gun = Agent(QNetworkTorch(4, 100, 100,  2))
    reward_gun = 0

    tank = Tank(screen, "neiro", (0, 1, 2, 3, 4), size=6,
            image=image_loader.tanks_images[1], cords=(BG_SIZE[0]*0.5, BG_SIZE[1]*0.5)
                )
    #list_of_zone = []
    #for _ in range(10):
        #list_of_zone.append()

    create_L_1(screen)
    #create_one_wall(screen)
    #create_multi_wall(screen)


    for _ in range(count_zones):
        CaptureZone(screen, cords=(BG_SIZE[0] * 0.5, BG_SIZE[1] * 0.1))

    zone = None
    if config_neural.NEAREST_TARGET_VALUE.type == config_neural.NEAREST_TARGET_VALUE.two_points:
        zone = CaptureZone.capture_zone_list[0]

    local_timer_sec = 0
    time_game = 0

    min_distance = 1000
    max_distance = 0



    CONST_SA = 25_000
    CONST_TR = CONST_SA
    timer_reward = CONST_TR
    count_step_alive = CONST_SA
    text_timer = f"таймер: {count_step_alive}"



    grid = GridSensor(screen, (0, 0), width_grid=config_neural.GRID_SENSOR.width_grid, height_grid=config_neural.GRID_SENSOR.height_grid, size_cell=config_neural.GRID_SENSOR.size_cell)

    #texts
    timer_T = Text(screen, cords=(BG_SIZE[0] * 0.8, BG_SIZE[1] * 0.05), name="timer", text=text_timer, size=50)

    #agent_tank.n_games += 1
    #n_game_T = Text(screen, cords=(BG_SIZE[0] * 0.05, BG_SIZE[1] * 0.05), name="n_game", text=f"раунд: {agent_tank.n_games}", size=50)

    score_T = Text(screen, cords=(BG_SIZE[0]*0.45, BG_SIZE[1] * 0.05), name="score", text=f"счёт: {tank.score}", size=50)



    #record_T = Text(screen, cords=(BG_SIZE[0] * 0.8, BG_SIZE[1] * 0.1), name="record", text=f"рекорд: {record_tank}",
    #               size=50)
    #rm - random move

    flag_rm_text_T = Text(screen, cords=(BG_SIZE[0] * 0.05, BG_SIZE[1] * 0.1), name="flag_rm_text",
                     text=f"режим:",
                     size=50)

    flag_rm_T = Text(screen, cords=(BG_SIZE[0] * 0.05, BG_SIZE[1] * 0.15), name="flag_rm", text=str(agent_tank.flag_training), size=50)
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


    start = True
    sum_reward_move = 0
    sum_reward_gun = 0
    sum_reward_capture_zone = 0
    count_gun = 0
    count_move = 0

    count_runs += 1




    os.makedirs(os.path.join(model_folder_path, experiment, model_saves_path, f"run_{count_runs}"), exist_ok=True)

    #profiler = Profiler()

    start_time = datetime.now()

    if flag_experiment_save:

        log_message = f"{start_time.strftime(DATE_PROJECT)}: Training starting..."
        print(log_message)
        write_log(log_message)

    #if not (config_neural.AGENT.input_type == config_neural.LIDAR.name):
    lidar_list_data = [0]*(len(Lidar.list_lidars)*2)





    #reward_move = max(-0.1, difference_distance)
    while True:

        #profiler.start()


        ticks = pygame.time.get_ticks()
        global_timer_sec = ticks // 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    start = True

                if event.key == pygame.K_x and agent_tank.flag_training:
                    #ic("explotatiom")
                    agent_tank.flag_training = False
                    if flag_draw:
                        flag_rm_T.update_text(text="Эксплуатация", color=RED_COLOR)
                elif event.key == pygame.K_x and not agent_tank.flag_training:
                    #ic("trining")
                    agent_tank.flag_training = True
                    if flag_draw:
                        flag_rm_T.update_text(text="тренировка", color=GREEN_COLOR)
                elif event.key == pygame.K_s:
                    agent_tank.model.save(experiment) #f"{local_timer_sec}"
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
                    #flag_rm_T.update_text(text="Эксплуатация", color=RED_COLOR)
                    score_T.update_text(f"счёт: {tank.score}")
                elif event.key == pygame.K_r:
                    agent_tank = Agent()
                    time_game = 0
                    tank.score = 0
                    tank.rect.x = BG_SIZE[0] * 0.5
                    tank.rect.y = BG_SIZE[1] * 0.5
                    agent_tank.flag_training = True
                    timer_T.update_text(f"время: {time_game}")
                    #flag_rm_T.update_text(text="тренировка", color=GREEN_COLOR)
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
        if flag_draw:
            screen.fill(bg_color)


        for bullet in Bullet.bullets:
            bullet.update()
            if flag_draw:
                bullet.draw()



        '''ist_zone = None
        zone: CaptureZone
        for zone in CaptureZone.capture_zone_list:
            zone.color = DARKENED_GREEN_COLOR
            if not ist_zone:
                ist_zone = zone
            else:
                if tank.compute_distance(zone) < tank.compute_distance(ist_zone):
                    ist_zone = zone
        zone = ist_zone
        zone.color = (0, 220, 0)'''




        #state_old = tank.get_data(zone, compute_distance_bullet(tank))

        state_old = input_type(tank, config_neural.AGENT.input_type, lidar_list_data, zone, grid.get_cells_state())
        #state_old_grid = grid.get_cells_state()

        #ic(state_old)
        #log(state_old)
        #print(state_old)
        #print(state_old)
        #print(tank.bullet)

        if flag_approach:
            old_distance = tank.compute_distance(zone)

        #print(state_old)
        #print("state_old[0:4]", state_old[0:4])


        #keys = agent_tank.get_action(state_old)
        #@ocurat_print()
        #keys_tank = agent_tank.get_action_stahiohastic(state_old)

        keys_tank = type_action(agent_tank, config_neural.AGENT.type_action)(state_old, epsilon)#agent_tank.get_action(state_old)

        #keys_tank = agent_tank.get_action_lite_random(state_old)
        #print(f"{keys_tank=}")
        #print(f"{keys_gun=}")
        #keys_tank.append(0)

        keys = keys_tank.copy()
        if not flag_train_gun:
            keys.append(0)


        #keys.append(keys_gun[1])
        #print(f"{keys=}")
        #print(f"{keys_gun=}")
        #print(f"{keys=}")



        #tank.update(keys)
        tank.update(keys_tank)

        if config_neural.AGENT.input_type == config_neural.LIDAR.name:
            lidar_list_data = []

            for lidar in Lidar.list_lidars:
                lidar.update()
                lidar.draw()
                size_lidar = lidar.size / lidar.distance

                #ic(pygame.Vector2(lidar.end_pos))

                lidar_list_data += [min(1, size_lidar), lidar.type_collide_obj] #,

        if config_neural.AGENT.input_type == config_neural.GRID_SENSOR.name:
            #if flag_draw:
                #grid.
            grid.update()



        #ic(lidar_list_data)

        #keys.pop()
        #print(f"reward_tank: {tank.reward_tank}")
        reward_tank = tank.reward

        #print(reward_tank)
        #no_revers_reward = local_timer_sec-CONST_SA
        if tank.flag_timer_reward:
            tank.flag_timer_reward = False
            timer_reward = CONST_TR
            #count_step_alive = CONST_SA





        #no_revers_reward = timer_reward-CONST_SA
        #print(f"{timer_reward=}")

        if flag_approach:
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

        if flag_approach:
            reward_tank += max(min_reward_approach, difference_distance)*k_size_reward_approach
        reward_tank += config_neural.FITNESS.step



        count_move += 1
        sum_reward_move += reward_tank
        #reward_tank += min(0.1, difference_distance)
        #reward_tank = reward_tank/1.5
        #reward_tank += no_revers_reward
        #print(f"{reward_tank=}")
        #points_in_second = tank.score / global_timer_sec
        #print(f"{points_in_second=}")


        #print(f"{tank.compute_distance(zone)}")
        if flag_draw:
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


        #state_new = tank.get_data(zone, compute_distance_bullet(tank))
        state_new = input_type(tank, config_neural.AGENT.input_type, lidar_list_data, zone, grid.get_cells_state())
        #ic(state_new)
        #state_new_grid = grid.get_cells_state()
        #ic(state_old_grid==state_new_grid)
        #state_new.pop()
        #print(f"{state_new=}")

        #print(f"len: {len(bufer_train_bullet)}")

        '''if agent_tank.flag_training:
            tank.score -= 1'''






        if agent_tank.flag_training:
            #state_new_gun = state_old[0:1]
            #state_new_gun.extend(state_new[1:])
            reward_gun = 0
            #if not state_old[-2]:
            #    reward_gun = 0.01

            #print(f"{state_old=}")
            #print(f"{state_new=}")
            #print(f"{state_new_gun=}")

            action_ind = keys_tank.index(1)
            state_old = torch.tensor(state_old, dtype=torch.float, device=device)  # .unsqueeze(dim=0)
            action_ind = torch.tensor(action_ind, dtype=torch.int64, device=device)  # .unsqueeze(dim=0)
            reward_tank = torch.tensor(reward_tank, dtype=torch.float, device=device)  # .unsqueeze(dim=0)
            state_new = torch.tensor(state_new, dtype=torch.float, device=device)  # .unsqueeze(dim=0)
            #done = torch.tensor(done).float()

            if keys[4]:
                reward_tank += GUN_FIT



            if keys[4] and False:
                #log(keys)
                reward_gun = 0


                #reward_tank = 0
                '''if state_old[-1] != -1:
                    reward_gun = -1'''
                '''if state_old[-2]:
                    reward_gun = -0.1
                    #print(f"{state_old=}")
                    #print(f"{reward_gun}")
                else:
                    reward_gun = -0.1'''

                '''if tank.flag_collide_bullet_zone:
                    reward_gun = tank.reward'''

                reward_gun = torch.tensor(reward_gun, dtype=torch.float, device=device)  # .unsqueeze(dim=0)
                    #print(reward_gun)

                '''sum_reward_gun += reward_gun
                state_new[-1] = 1
                state_new_gun = state_old[0:1]
                state_new_gun.extend(state_new[1:])'''
                #print(f"{state_old=}")
                #print(f"{state_new_gun=}")

                '''bufer_train_bullet.append(
                    ([state_old, action_ind, torch.tensor(1, dtype=torch.float), state_new, done], tank.bullet) #max(1, min(1200, tank.compute_distance(zone) - 600+600)/2)
                                          )'''
                #print(state_old, keys, reward_tank, state_new, done)

                #log(reward_gun)
                agent_tank.train_short_memory(state_old, action_ind, reward_gun, state_new, done)
                if flag_train_long_memory:
                    agent_tank.remember(state_old, action_ind, reward_gun, state_new, done)

            # тренировка короткой памяти
            #print(state_new_gun)
            #print(f"{keys_tank=}")
            if tank.flag_collide_bullet_zone:
                tank.flag_collide_bullet_zone = False
                #agent_tank.train_short_memory(state_old, action_ind, torch.tensor(1, dtype=torch.float, device=device), state_new, done)
                #ic(tank.flag_collide_bullet_zone)


            if flag_train_short_memory:
                agent_tank.train_short_memory(state_old, action_ind, reward_tank, state_new, done)

            if flag_train_long_memory:
                agent_tank.remember(state_old, action_ind, reward_tank, state_new, done)
            #agent_gun.train_short_memory(state_old, keys_gun, reward_gun, state_new_gun, done)

            if tank.flag_reward_capture_zone:
                tank.flag_reward_capture_zone = False
                sum_reward_capture_zone += tank.reward

                #count_step_alive = 0

        if count_train_target_steps >= const_train_target_step:
            target_dqn.load_state_dict(policy_dqn.state_dict())
            count_train_target_steps = 0


        if count_action_steps_train >= const_action_step_train:
            agent_tank.n_games += 1
            count_action_steps_train = 0
            #print(f"{agent_tank.n_games=}")
            #log(agent_tank.n_games)

            #ic(tank.score)
            #ic(agent_tank.n_games)

            if flag_experiment_save:
                if agent_tank.n_games % episode_step == 0 and agent_tank.n_games:
                    if not flag_debug:
                        DATE_FORMAT_2 = datetime.now().strftime("%d-%m %H:%M:%S")
                        ic.configureOutput(prefix=f'{DATE_FORMAT_2} | ', includeContext=flag_debug)

                    ic(tank.score)

                    ic(count_episodes)

                    episodes_score.append(tank.score)

                    #epsilon = max(epsilon * epsilon_decay, epsilon_min)


                    epsilon_history.append(epsilon)

                    save_graph((epsilon_history, episodes_score))
                    write_info_runs(count_runs, count_steps, count_episodes, record_tank, epsilon)

                    if record_tank < tank.score:
                        best_record = record_tank
                        record_tank = tank.score

                        if not best_record:
                            best_record = -1

                        ic(record_tank)
                        agent_tank.model.save(count_runs, experiment, meta=f"steps-{count_steps}-episode-{count_episodes}-record-{record_tank}")


                        log_message = f"{datetime.now().strftime(DATE_FORMAT)}: New best record {record_tank:0.1f} ({(record_tank - best_record) / best_record * 100:+.1f}%) at episode {count_episodes}, step {count_steps}, saving model..."
                        print(log_message)
                        write_log(log_message)


                    tank.score = 0

                    count_episodes += 1

                    ic("new episode...")

                if agent_tank.n_games % save_model_step == 0:
                    agent_tank.model.save(count_runs, experiment, meta=f"steps-{count_steps}")
                    #log_message = f"{datetime.now().strftime(DATE_FORMAT)}: count steps {count_steps} epidode {count_episodes}  saving model..."
                    #print(log_message)
                    #write_log(log_message)
                    #write_info_runs(count_runs, count_steps, count_episodes, record_tank)






        #print(reward_tank)

        #print(f"len={len(bufer_train_bullet)}")
        if tank.flag_collide_bullet_zone and False:
            tank.flag_collide_bullet_zone = False
            for state_bullet in bufer_train_bullet:
                if state_bullet[1] is tank.bullet:
                    # state_bullet[0][2] = tank.reward_tank
                    state_old, keys_gun, reward_gun, state_new, done = state_bullet[0]
                    # agent_gun.train_short_memory(state_old, keys_gun, reward_tank, state_new, done)
                    # agent_gun.remember(state_old, keys_gun, reward_gun, state_new, done)
                    # print(f"reward_gun bullet distance: {reward_gun}")
                    agent_tank.train_short_memory(state_old, keys_gun, reward_tank, state_new, done)
                    agent_tank.remember(state_old, keys_gun, reward_gun, state_new, done)
                    sum_reward_gun += reward_gun
                    count_gun += 1
                    # bufer_train_bullet_memory.append(state_bullet[0])
                    # print(f"tank.bullet {tank.bullet}")
                    # print(state_bullet)
                    # print("======================")
                    # print(f"{state_old=}")
                    # print(f"{state_new=}")
                    # print(f"{keys_gun=}")
                    # print(f"{keys=}")
                    # print(f"{reward_gun=}")
                    # print("======================")
                    break

            bufer_train_bullet = []

        if count_step_train_long_memory >= const_train_long_memory and all((count_step_train_long_memory, flag_train_long_memory, agent_tank.flag_training)):
            #ic("start training...")

            epsilon = max(epsilon * epsilon_decay, epsilon_min)

            agent_tank.train_long_memory()
            #ic("training...")
            #ic(count_steps)
            #ic("end training...")

            #flag_train_long_memory = False
            #print(f"{count_move=}")
            #print(f"{count_gun=}")
            count_step_train_long_memory = 0

        #print(f"{sum_reward_move=}")
        #print(f"{sum_reward_gun=}")









        if local_timer_sec != global_timer_sec:
            local_timer_sec = global_timer_sec
            time_game += 1

            #timer_T.update_text(f"таймер: {count_step_alive}")
            #count_step_alive -= 1
            if flag_draw:
                timer_T.update_text(f"время: {time_game}")
            timer_reward += TIME_FIT
            #ic(count_action_steps_train)
            #flag_train_long_memory = True
            #ic(sum_reward_capture_zone)
            #ic(sum_reward_move)
            if flag_print_fps:
                real_time_fps = clock.get_fps()
                ic(real_time_fps)



            #print(local_timer_sec)


        if count_step_alive > CONST_SA:
            count_step_alive = 0

            """for wall in Wall.walls_list:
                wall.update()"""

            capture_zone: CaptureZone
            for capture_zone in CaptureZone.capture_zone_list:
                capture_zone.collide()

            tank.rect.x = BG_SIZE[0] * 0.5
            tank.rect.y = BG_SIZE[1] * 0.5

        if flag_draw:
            tank.draw()
        '''for zone_d in list_of_zone:
            zone_d.draw()'''
        #zone.draw()
        for block in Block.blocks:
            if flag_draw:
                block.draw()

        if flag_draw:
            if tank.capture_zone:
                tank.capture_zone.color = (0, 220, 0)
                tank.capture_zone.surface.fill(tank.capture_zone.color)
                tank.capture_zone.screen.blit(tank.capture_zone.surface, tank.capture_zone.rect)

        if flag_draw:

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
        if flag_draw:
            pygame.display.flip()
        #clock.tick(target_fps)

        #tank.score = 0
        if not agent_tank.flag_training:
            #clock.tick(target_fps)
            clock.tick()
        else:
            clock.tick()
        #real_time_fps = clock.get_fps()
        #print(f"{real_time_fps=}")
        if flag_draw:
            #fps_T.update_text(f"fps: {real_time_fps:.1f}")
            pass
        # clock.tick(300)
        # clock.tick()
        #print(f"{real_time_fps=}")
        if agent_tank.flag_training:
            count_train_target_steps += 1
            count_action_steps_train += 1
            count_step_alive += 1
            if flag_train_long_memory:
                count_step_train_long_memory += 1

            count_steps += 1

        if done:
            # train long memory, plot result
            #game.reset()
            #zone.collide()# = CaptureZone(screen, cords=(BG_SIZE[0] * 0.5, BG_SIZE[1] * 0.1))

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

            count_step_alive = CONST_SA

            #timer_T.update_text(f"таймер: {count_step_alive}")
            #timer_T.update_text(f"время: 0")
            #n_game_T.update_text(f"раунд: {agent_tank.n_games}")

            if record_tank < tank.score:
                record_tank = tank.score

                #record_T.update_text(f"рекорд: {record_tank}")
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
        #profiler.stop()
        #print(profiler.output_text(unicode=True, color=True))


if __name__ == '__main__':
    train()