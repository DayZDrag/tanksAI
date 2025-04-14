import pygame
import os

from config.config import Config

class ImageLoader:
    def __init__(self):

        self.config = Config()
        self.images_dir = self.config.images_dir
        self.tanks_images = self.load_tank_images()

    def load_tank_images(self):
        return [pygame.image.load(os.path.join(self.config.base_dir, self.images_dir, 'tanks', img)) for img in os.listdir(os.path.join(self.config.base_dir, self.images_dir, 'tanks'))]
        #return [pygame.image.load(os.path.join(self.images_dir, 'tanks', img)) for img in
        #        os.listdir(os.path.join(self.images_dir, 'tanks'))]

image_loader = ImageLoader()