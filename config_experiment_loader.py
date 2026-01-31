from types import SimpleNamespace
import yaml
import os

from config_game import experiment


class ExperimentConfig(SimpleNamespace):
    experiment: str
    name_load_model: str
    path_run: int
    flag_load_latest_model: bool
    flag_load_model: bool
    flag_experiment_save: bool
    flag_draw: bool

class EnvironmentConfig(SimpleNamespace):
    count_zones: int


class TrainConfig(SimpleNamespace):
    save_model_step: int
    episode_step: int


class ConfigExperimentLoader:
    def __init__(self, path="config_experiment.yml"):
        self.config = self.load_config(path)

        exp = self.config["experiment"]
        env = exp["environment"]
        train = exp["train"]

        self.EXPERIMENT = ExperimentConfig(
            experiment=exp["experiment"],
            name_load_model=exp["name_load_model"],
            path_run=exp["path_run"],
            flag_load_latest_model=exp["flag_load_latest_model"],
            flag_load_model=exp["flag_load_model"],
            flag_experiment_save=exp["flag_experiment_save"],
            flag_draw=exp["flag_draw"]
        )

        self.ENVIRONMENT = EnvironmentConfig(
            count_zones=env["count_zones"]
        )

        self.TRAIN = TrainConfig(
            save_model_step=train["save_model_step"],
            episode_step=train["episode_step"]
        )

    def load_config(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file {path} not found")
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def get_config(self):
        return self.config

# Использование
config_experiment = ConfigExperimentLoader(path = os.path.join("saves", experiment, "config_experiment.yml"))