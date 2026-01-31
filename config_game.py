from datetime import datetime

import pygame
import torch
import os
import shutil

from icecream import ic

experiment = "lidar_sensor_test_199"
model_folder_path = 'saves'
model_saves_path = "saves"

folder = os.path.join(model_folder_path, experiment, model_saves_path)
os.makedirs(folder, exist_ok=True)


if not os.path.isfile(os.path.join(model_folder_path, experiment, "config_neural.yml")):
    shutil.copy("config_neural.yml", os.path.join(model_folder_path, experiment, "config_neural.yml"))

if not os.path.isfile(os.path.join(model_folder_path, experiment, "config_experiment.yml")):
    shutil.copy("config_experiment.yml", os.path.join(model_folder_path, experiment, "config_experiment.yml"))


from config_experiment_loader import config_experiment

name_load_model = config_experiment.EXPERIMENT.name_load_model#"model_steps-8785000"
flag_load_last_model = config_experiment.EXPERIMENT.flag_load_latest_model
flag_load_model = config_experiment.EXPERIMENT.flag_load_model
flag_experiment_save = config_experiment.EXPERIMENT.flag_experiment_save

count_zones = config_experiment.ENVIRONMENT.count_zones

save_model_step = config_experiment.TRAIN.save_model_step
episode_step = config_experiment.TRAIN.episode_step


from config_neural_loader import config_neural
#colors
DARKENED_GREEN_COLOR = (0, 146, 0)
RED_COLOR = (255, 10, 0)
ORANGE_COLOR = (222, 143, 0)
GREEN_COLOR = (63, 255, 82)
WHITE_COLOR = (255, 255, 255)
BLACK_COLOR = (0, 0, 0)



#fitness
CAPTURE_ZONE_FIT = config_neural.FITNESS.capture_zone
DEATH_FIT = config_neural.FITNESS.death
TIME_FIT = config_neural.FITNESS.time
CAPTURE_BULLET_FIT = config_neural.FITNESS.capture_bullet

flag_approach = config_neural.APPROACH.activate
k_size_reward_approach = config_neural.APPROACH.k_size_reward
min_reward_approach = config_neural.APPROACH.min_reward

GUN_FIT = config_neural.FITNESS.gun
#pygame
BG_SIZE = (1200, 800)
#screen = pygame.display.set_mode(BG_SIZE)
FULL_SCREEN = (1550, 810)
#bg_size = (1200, 800)
# bg_size = FULL_SCREEN
bg_rect = pygame.Rect(0, 0, BG_SIZE[0], BG_SIZE[1])
bg_color = (255, 184, 74)
#darkened_green_color = (0, 146, 0)
#RED_color = (255, 10, 0)

#bg = pygame.image.load(os.path.join(config.images_dir, "fon.png")).convert()
#bg = pygame.transform.scale(bg, BG_SIZE)

#clock = pygame.time.Clock()
target_fps = 60

flag_draw = config_experiment.EXPERIMENT.flag_draw


flag_print_fps = False
flag_debug = False

DATE_FORMAT = "%d-%m-%Y %H:%M:%S"
DATE_PROJECT = datetime.now().strftime(DATE_FORMAT)
debug = "DEBUG"
prefix = DATE_PROJECT

if flag_debug:
    prefix = debug

device = 'cuda' if torch.cuda.is_available() else 'cpu'
device = "cpu"
#done = False

MAX_MEMORY = config_neural.AGENT.max_memory
BATCH_SIZE = config_neural.AGENT.batch_size
LR = config_neural.AGENT.lr

flag_train_gun = config_neural.FLAGS.train_gun

size_input = config_neural.MODEL.size_input
size_hidden = config_neural.MODEL.size_hidden
size_output = config_neural.MODEL.size_output + flag_train_gun

enable_dueling_dqn = config_neural.MODEL.enable_dueling_dqn
flag_noise_bias = config_neural.MODEL.noise_bias


epsilon_decay = config_neural.GET_ACTION_EPSILON.epsilon_decay
epsilon_min = config_neural.GET_ACTION_EPSILON.epsilon_min
