import pygame

from config_game import BLACK_COLOR, WHITE_COLOR, GREEN_COLOR, flag_draw, ORANGE_COLOR


class GridSensor:
    grid_list = []
    def __init__(self, screen, pos,  width_grid, height_grid, size_cell, obj=None):
        GridSensor.grid_list.append(self)


        self.screen = screen

        self.width_grid = width_grid
        self.height_grid = height_grid
        self.size_cell = size_cell

        #self.color =

        self.pos = pos

        self.x_grid = pos[0]
        self.y_grid = pos[1]

        from tank import Tank
        self.obj: Tank = obj

        self.rect_grid = pygame.Rect(self.x_grid, self.y_grid, self.width_grid, self.height_grid)

        self.cells_list = []

        self.generate_cells()

        #self.surface = pygame.Surface((self.width, self.height))
        #self.surface.fill(self.color)

    def update(self):
        from tank import Tank
        from block import Wall, CaptureZone
        from bullet import Bullet


        objects =   Bullet.bullets + Wall.walls_list + CaptureZone.capture_zone_list + Tank.tanks

            #ic("=======================")
        for cell in self.cells_list:
            cell["activate"] = 0
            for obj in objects:
                if not hasattr(obj, 'rect'):
                    continue
                # cell: pygame.Rect
                # if cell.colliderect(obj.rect):
                #    cell.occupied = True  # Или как там у тебя будет обозначаться "занятость"
                #    #print(f"{cell.colliderect(obj.rect)=}")
                #    #print(f"{obj.rect=}")
                #    #print(f"{cell=}")
                #    pygame.draw.rect(self.screen, (255, 0, 0), cell)
                # print(f"{obj.rect=}")
                if obj.rect.colliderect(cell["rect"]):


                    if isinstance(obj, Wall):
                        cell["activate"] = max(cell["activate"], 0.6)
                        if flag_draw:
                            pygame.draw.rect(self.screen, ORANGE_COLOR, cell["rect"])
                    elif isinstance(obj, CaptureZone):  # Bullet/Wall
                        cell["activate"] = max(cell["activate"], 0.3)
                        if flag_draw:
                            pygame.draw.rect(self.screen, WHITE_COLOR, cell["rect"])
                    elif isinstance(obj, Tank):
                        cell["activate"] = max(cell["activate"], 1)
                        if flag_draw:
                            pygame.draw.rect(self.screen, GREEN_COLOR, cell["rect"])




                #ic(self.cells_list)
                    #self.cells_list = self.cells_list


                    #ic(obj)
                    #ic(cell)


                    #ic(cell["activate"])
                #ic("=======================")

    def get_cells_state(self):
        return [cell["activate"] for cell in self.cells_list]




    def generate_cells(self):
        for x in range(self.width_grid//self.size_cell):
            for y in range(self.height_grid//self.size_cell):
                rect = pygame.Rect(x*self.size_cell, y*self.size_cell, self.size_cell, self.size_cell)
                self.cells_list.append({"rect": rect, "activate": 0})




    def draw(self):
        for cell in self.cells_list:
            #cell_surf = pygame.Surface((self.size_cell, self.size_cell))
            #self.screen.blit(cell_surf, cell.rect)
            pygame.draw.rect(self.screen, BLACK_COLOR, cell["rect"])
