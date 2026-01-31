import os
from types import SimpleNamespace
import yaml
from typing import cast

from icecream import ic
from config_game import experiment

class AgentConfig(SimpleNamespace):
    max_memory: int
    batch_size: int
    lr: float
    gamma: float
    type_action: str
    input_type: str

class GetActionConfig(SimpleNamespace):
    name: str

class GetActionRandomConfig(SimpleNamespace):
    name: str

    K_len_learn: int
    proc_rand: int

class GetActionLiteRandomConfig(SimpleNamespace):
    name: str

    proc_rand: float

class GetActionStahiohasticConfig(SimpleNamespace):
    name: str

    temperature: float

class GetActionEpsilonConfig(SimpleNamespace):
    name: str

    epsilon_init: float
    epsilon_decay: float
    epsilon_min: float


class ConstConfig(SimpleNamespace):
    train_target_step: int
    action_step_train: int
    train_long_memory: int

class FlagsConfig(SimpleNamespace):
    train_long_memory: bool
    train_short_memory: bool
    train_gun: bool

class ModelConfig(SimpleNamespace):
    size_input: int
    size_hidden: int
    size_output: int
    enable_dueling_dqn: bool
    enable_double_dqn: bool
    noise_bias: bool

class FitnessConfig(SimpleNamespace):
    capture_zone: float
    death: float
    time: float
    capture_bullet: float
    step: float
    gun: float


class ApproachConfig(SimpleNamespace):
    activate: bool
    k_size_reward: int
    min_reward: float

class LidarConfig(SimpleNamespace):
    name: str

    mirrored: bool
    rotate: bool
    level: int
    distance: float
    start_angle: int

class NearestTargetValueConfig(SimpleNamespace):
    name: str

    type: str

    two_points: str
    angle_and_distance: str

class GridSensorConfig(SimpleNamespace):
    name: str

    size_cell: int
    width_grid: int
    height_grid: int

class ConfigNeuralLoader:
    def __init__(self, path):
        self.config = self.load_config(path)

        agent = self.config["agent"]

        self.AGENT = AgentConfig(
            max_memory=agent["max_memory"],
            batch_size=agent["batch_size"],
            lr=agent["lr"],
            gamma=agent["gamma"],
            type_action=agent["type_action"],
            input_type=agent["input_type"],
        )

        self.GET_ACTION = GetActionConfig(
            name="get_action"
        )

        self.GET_ACTION_RANDOM = GetActionRandomConfig(
            name="get_action_random",



            K_len_learn=agent["get_action_random"]["K_len_learn"],
            proc_rand=agent["get_action_random"]["proc_rand"]
        )

        self.GET_ACTION_LITE_RANDOM = GetActionLiteRandomConfig(
            name="get_action_lite_random",

            proc_rand=agent["get_action_lite_random"]["proc_rand"]
        )

        self.GET_ACTION_STAHIOHASTIC = GetActionStahiohasticConfig(
            name="get_action_stahiohastic",

            temperature=agent["get_action_stahiohastic"]["temperature"]
        )

        self.GET_ACTION_EPSILON = GetActionEpsilonConfig(
            name="get_action_epsilon",

            epsilon_init=agent["get_action_epsilon"]["epsilon_init"],
            epsilon_decay=agent["get_action_epsilon"]["epsilon_decay"],
            epsilon_min=agent["get_action_epsilon"]["epsilon_min"]
        )

        self.CONST = ConstConfig(
            train_target_step=agent["const"]["train_target_step"],
            action_step_train=agent["const"]["action_step_train"],
            train_long_memory=agent["const"]["train_long_memory"]
        )

        self.FLAGS = FlagsConfig(
            train_long_memory=agent["flags"]["train_long_memory"],
            train_short_memory=agent["flags"]["train_short_memory"],
            train_gun=agent["flags"]["train_gun"]
        )

        self.MODEL = ModelConfig(
            size_input=agent["model"]["size_input"],
            size_hidden=agent["model"]["size_hidden"],
            size_output=agent["model"]["size_output"],
            enable_dueling_dqn=agent["model"]["enable_dueling_dqn"],
            enable_double_dqn=agent["model"]["enable_double_dqn"],
            noise_bias=agent["model"]["noise_bias"],
        )

        self.FITNESS = FitnessConfig(
            capture_zone=agent["fitness"]["capture_zone"],
            death=agent["fitness"]["death"],
            time=agent["fitness"]["time"],
            capture_bullet=agent["fitness"]["capture_bullet"],
            step=agent["fitness"]["step"],
            gun=agent["fitness"]["gun"],

        )
        self.APPROACH = ApproachConfig(
            activate=agent["fitness"]["approach"]["activate"],
            k_size_reward=agent["fitness"]["approach"]["k_size_reward"],
            min_reward=agent["fitness"]["approach"]["min_reward"]
        )


        self.LIDAR = LidarConfig(
            name="lidar",

            mirrored=agent["lidar"]["mirrored"],
            rotate=agent["lidar"]["rotate"],
            level=agent["lidar"]["level"],
            distance=agent["lidar"]["distance"],
            start_angle=agent["lidar"]["start_angle"]
        )
        self.NEAREST_TARGET_VALUE = NearestTargetValueConfig(
            name="nearest_target_value",

            type=agent["nearest_target_value"]["type"],

            two_points="two_points",
            angle_and_distance="angle_and_distance",

        )

        self.GRID_SENSOR = GridSensorConfig(
            name="grid_sensor",

            size_cell=agent["grid_sensor"]["size_cell"],
            width_grid=agent["grid_sensor"]["width_grid"],
            height_grid=agent["grid_sensor"]["height_grid"],
        )


    def load_config(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file {path} not found")
        with open(path, "r") as f:
            return yaml.safe_load(f)


    def get_config(self):
        return self.config

config_neural = ConfigNeuralLoader(path = os.path.join("saves", experiment, "config_neural.yml"))