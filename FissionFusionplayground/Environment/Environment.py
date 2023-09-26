from Animals.Agents import *
from Animals.Enemies import *
from Environment.Grass import Grass
from Animals.States import DeadState
from Animals.States.AgentStates import *
from Animals.States.EnemyStates import *

import pygame
import sys
import numpy as np
from tqdm import tqdm


class Environment:
    GRASS_COLOR = (50, 150, 50)
    GRID_COLOR = (0, 0, 0)
    FLOOR_COLOR = (255, 255, 200)
    FLOOR_NEXT_COL = (0, 0, 255)
    WANDERING_COLOR = (0, 0, 200)
    ANIMAL_COLOR = (115, 75, 54)
    HUNGRY_COLOR = (186, 120, 69)
    EATING_COLOR = (200, 191, 231)
    ENEMY_COLOR = (200, 0, 0)
    DEAD_COLOR = (0, 0, 0)

    def __init__(self, width=160, height=120, cell_size=Animal.Animal.RADIUS*1.8):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.next_animal_id = 0

        self.screen_height = height * self.cell_size
        self.screen_width = width * self.cell_size
        self.screen = None
        self.clock = None

        self.animals = []
        self.enemies = []
        self.grass = {}

        self.generate_grass()
        self.generate_animals()

    def generate_animals(self, num_cycles=25, min_num=60):
        self.animals = []

        # use a generative algorithm to randomly spawn animal positions
        animal_positions = self._random_generation(num_cycles=num_cycles,
                                                   progress_bar='Generating Animals...',
                                                   stop_threshold=min_num + 15,
                                                   edges=False)

        # create animal objects for each generated animal position
        i = 0
        for row, col in np.ndindex(*animal_positions.shape):
            if animal_positions[row, col] == 1:
                position = (row * self.cell_size + self.cell_size / 2,
                            col * self.cell_size + self.cell_size / 2)

                self.animals.append(Agent(environment=self,
                                          x=position[0], y=position[1],
                                          theta=np.random.uniform(low=-np.pi, high=np.pi)))
                i += 1
            if i == 50: break           # this line can be used to set a limit on the number of animals
                                        # actually created

        # generate enemies, the number of is specified here
        self.generate_enemies(5)




    def generate_grass(self, num_cycles=10):
        self.grass = {}

        # use a generation algorithm to randomly generate grass positions
        grass_positions = self._random_generation(num_cycles=num_cycles,
                                                  progress_bar='Generating Environment...',
                                                  edges=True)

        # create grass objects for each grass position
        for row, col in np.ndindex(*grass_positions.shape):
            if grass_positions[row,col] == 1:
                grass_pos = (int(row * self.cell_size), int(col * self.cell_size))
                self.grass[grass_pos] = Grass(pos=grass_pos,
                                              cell_size=self.cell_size)


    # randomly spawn enemies in positions according to a uniform distribution
    def generate_enemies(self, number):
        if self.enemies is None:
            self.enemies= []

        for i in range(number):
            self.enemies.append(Enemy(environment=self,
                                      x=np.random.uniform(low=0, high=self.screen_width),
                                      y=np.random.uniform(low=0, high=self.screen_height),
                                      theta=np.random.uniform(low=-np.pi, high=np.pi)))



    # generates random patterns. Used in generating animal and grass positions
    def _random_generation(self, progress_bar, num_cycles, probs=(0.45, 0.55),
                           edges=True, stop_threshold=0):
        cells = np.random.choice(2, size=(self.height, self.width), p=probs)

        for i in tqdm(range(num_cycles), progress_bar):
            num_blocks = np.sum(cells)
            if num_blocks <= stop_threshold:
                break
            reset_edges = edges
            if i / num_cycles > 0.6:
                reset_edges = False
            cells = self._generative_cycle(cells, reset_edges)
        return cells



    # helper function for random generation algorithm
    def _generative_cycle(self, world_map, edges=True):
        # Create temporary matrix of zeros
        temp = np.zeros((world_map.shape[0], world_map.shape[1]))

        for row, col in np.ndindex(world_map.shape):
            walls = np.sum(world_map[row - 1:row + 2, col - 1:col + 2]) - world_map[row, col]

            # Apply rules (if more than 4 walls create a wall, else a floor)
            if walls > 4:
                temp[row, col] = 1

        # Set borders to walls
        if edges:
            temp[0:self.height, 0] = 1
            temp[0, 0:self.width] = 1
            temp[0:self.height, self.width - 1] = 1
            temp[self.height - 1, 0:self.width] = 1

        return temp



    # iniitalizes and opend pygame window
    def start_animation(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width * self.cell_size,
                                               self.height * self.cell_size))
        self.clock = pygame.time.Clock()
        self.update_animation()


    # blitz to the screen all updated all agents, grass, and enemies in their current positions
    def update_animation(self, draw_info=False):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

        self.screen.fill(Environment.FLOOR_COLOR)

        for grass_pos in self.grass:
            # draw grass
            grass_obj = self.grass[grass_pos]
            if grass_obj.animal is not None:
                grass_color = tuple(np.array(Environment.ENEMY_COLOR) +
                                    (np.array(Environment.FLOOR_COLOR) -
                                    np.array(Environment.ENEMY_COLOR)) * (1 - grass_obj.size))
            elif len(grass_obj.locked_on_animals) > 0:
                grass_color = tuple(np.array(Environment.WANDERING_COLOR) +
                                    (np.array(Environment.FLOOR_COLOR) -
                                    np.array(Environment.WANDERING_COLOR)) * (1 - grass_obj.size))
            else:
                grass_color = tuple(np.array(Environment.GRASS_COLOR) +
                                    (np.array(Environment.FLOOR_COLOR) -
                                     np.array(Environment.GRASS_COLOR)) * (1 - grass_obj.size))

            # Draw rectangles, using as background the screen value.
            pygame.draw.rect(self.screen, grass_color, (grass_obj.y, grass_obj.x,
                             self.cell_size - 1, self.cell_size - 1))

        for animal in self.animals + self.enemies:
            animal_color = Environment.ANIMAL_COLOR
            if isinstance(animal.state, DeadState.DeadState):
                animal_color = Environment.DEAD_COLOR
            elif animal.is_enemy:
                animal_color = Environment.ENEMY_COLOR
            else:
                if isinstance(animal.state, FindFoodState.FindFoodState):
                    animal_color = Environment.WANDERING_COLOR
                elif isinstance(animal.state, WanderingState.WanderingState):
                    animal_color = Environment.WANDERING_COLOR
                elif isinstance(animal.state, EatingState.EatingState):
                    animal_color = Environment.EATING_COLOR

            pygame.draw.circle(surface=self.screen,
                               color=animal_color,
                               center=(animal.position[1], animal.position[0]),
                               radius=Animal.Animal.RADIUS * (1 + (animal.size - 1) / 2))

            if animal.is_enemy:
                pygame.draw.circle(surface=self.screen,
                                   color=(0,0,0),
                                   center=(animal.position[1], animal.position[0]),
                                   radius=animal.visible_distance,
                                   width=1)

                if not isinstance(animal.state, DeadState.DeadState):
                    if draw_info:
                        font = pygame.font.Font(None, 12)
                        text = font.render(f"hunger: {'{:.4f}'.format(animal.hunger)} " +
                                           f"health: {'{:.4f}'.format(animal.health)}", True, (0,0,0))
                        text_rect1 = text.get_rect()
                        text_rect1.center = (animal.position[1], animal.position[0] - text_rect1.height)
                        self.screen.blit(text, text_rect1)

                        text = font.render(f"stamina: {'{:.4f}'.format(animal.stamina)} " +
                                           f"exhausted: {animal.exhausted}", True, (0,0,0))
                        text_rect2 = text.get_rect()
                        text_rect2.center = (animal.position[1], animal.position[0] - text_rect1.height - text_rect2.height)
                        self.screen.blit(text, text_rect2)

                        text = font.render(f"state: {str(animal.state)}", True, (0,0,0))
                        text_rect3 = text.get_rect()
                        text_rect3.center = (animal.position[1], animal.position[0] - \
                                             text_rect1.height - text_rect2.height - text_rect3.height)
                        self.screen.blit(text, text_rect3)

            if isinstance(animal.state, DeadState.DeadState):
                if draw_info:
                    font = pygame.font.Font(None, 12)
                    text = font.render(f"size: {'{:.4f}'.format(animal.size)} ", True, (0, 0, 0))
                    text_rect = text.get_rect()
                    text_rect.center = (animal.position[1], animal.position[0] + text_rect.height)
                    self.screen.blit(text, text_rect)

            elif isinstance(animal.state, EatingState.EatingState):
                pass
                # font = pygame.font.Font(None, 12)
                # text = font.render(f"Position: {animal.position} ", True, (0, 0, 0))
                # text_rect = text.get_rect()
                # text_rect.center = (animal.position[1], animal.position[0] + text_rect.height)
                # self.screen.blit(text, text_rect)
                #
                # font = pygame.font.Font(None, 12)
                # text = font.render(f"Food position: {animal.curr_eating.pos()} ", True, (0, 0, 0))
                # text_rect = text.get_rect()
                # text_rect.center = (animal.position[1], animal.position[0] + 2*text_rect.height)
                # self.screen.blit(text, text_rect)

        pygame.display.update()
        return True


    # exits the animation
    def end_animation(self):
        pygame.quit()