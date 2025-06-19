import pygame

#colors
DARKENED_GREEN_COLOR = (0, 146, 0)
RED_COLOR = (255, 10, 0)
ORANGE_COLOR = (222, 143, 0)
GREEN_COLOR = (63, 255, 82)



#fitness
CAPTURE_ZONE_FIT = 0
DEATH_FIT = -5
TIME_FIT = 0
CAPTURE_BULLET_FIT = 0
#pygame
BG_SIZE = (1200, 800)
#screen = pygame.display.set_mode(BG_SIZE)
FULL_SCREEN = (1550, 810)
#bg_size = (1200, 800)
# bg_size = FULL_SCREEN

bg_color = (255, 184, 74)
#darkened_green_color = (0, 146, 0)
#RED_color = (255, 10, 0)

#bg = pygame.image.load(os.path.join(config.images_dir, "fon.png")).convert()
#bg = pygame.transform.scale(bg, BG_SIZE)

#clock = pygame.time.Clock()
target_fps = 60