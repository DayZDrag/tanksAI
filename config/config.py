import json
import os

project_dir = "tanksAI"
config_dir = "config"
config_file = "config.json"


class Config:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_dir = self._get_dir_project()

        self.config_dir = os.path.join(self.project_dir, config_dir)
        self.config_path = os.path.join(self.config_dir, config_file)
        self.config = self._load_config()

        self.images_dir = self._resolve_path("images_dir")
        self.model_dir = self._resolve_path("model_dir")


    def _load_config(self):
        """Загружает конфигурацию из JSON-файла."""
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _resolve_path(self, key):
        """Возвращает путь на основе project_dir."""
        return os.path.join(self.project_dir, self.config[key])

    def _get_dir_project(self):
        current_path = self.base_dir
        while True:
            if os.path.basename(current_path) == project_dir:
                return current_path
            current_path = os.path.dirname(current_path)



#print(Config().images_dir)