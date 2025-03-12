import pygame
from config_game import screen

class Text:
    texts = []
    def __init__(self, screen, cords, name, font=None, size=74, text="test text", color=(255, 255, 255)):
        Text.texts.append(self)

        self.screen = screen
        self.name = name
        self.color = color

        self.x = cords[0]
        self.y = cords[1]

        self.font = pygame.font.Font(font, size)
        self.surface = self.font.render(text, True, color)

    def update_text(self, text):
        self.surface = self.font.render(text, True, self.color)


    def draw(self):
        self.screen.blit(self.surface, (self.x, self.y))

class Point:
    points = []
    def __init__(self, name, text, cords, score=0):
        Point.points.append(self)

        self.name = name
        self.score = score
        self.text = text
        self.cords = cords
        self.text_obj = Text(screen, cords=cords, name=name, text=f"{text}:{self.score}", size=50)

    def update(self, score):
        self.score = score
        self.text_obj.update_text(f"{self.text}:{score}")