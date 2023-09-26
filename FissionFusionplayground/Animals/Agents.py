from Animals.Enemies import *
from Animals.States.AgentStates.HerdState import *
from Animals.States.AgentStates.WanderingState import *

import numpy as np


class Agent(Animal.Animal):
    def __init__(self, environment, x, y, theta):
        Animal.Animal.__init__(self, environment=environment, x=x, y=y, theta=theta,
                               speed=np.random.uniform(low=2, high=4),
                               size=np.random.uniform(low=0.8, high=1.4),
                               coasting_speed=np.random.uniform(low=4, high=5),
                               running_speed=np.random.uniform(low=14, high=21),
                               standard_acceleration=np.random.uniform(low=1, high=3),
                               max_acceleration=np.random.uniform(low=6, high=8),
                               metabolism=np.random.uniform(low=0.002, high=0.004),
                               fill_rate=np.random.uniform(low=1.4, high=1.8),
                               max_stamina=np.random.uniform(low=1.2, high=1.4),
                               visible_distance=np.random.uniform(low=120, high=150),
                               visible_angle=np.random.uniform(low=3*np.pi/4, high=5*np.pi/6),
                               starting_state=HerdState.HerdState(self),
                               is_enemy=False)


        self.dominance = 1 + np.random.exponential(scale=1)
        if self.dominance > 4:
            self.visible_distance += 100
        self.orientation_zone = np.random.uniform(low=30, high=45)
        self.repulsion_to_enemies_zone = np.random.uniform(low=80, high=self.visible_distance)

        self.preferred_grass = None
        self.preferred_grass_score = -np.inf

        self.locked_on_grass = None
        self.locked_on_grass_score = -np.inf
        self.visible_grass = []

    def calc_next(self, dt):
        self.next_position, self.next_theta, self.next_speed, self.next_state = self.state.transition_logic()

    def attraction_to_center(self):
        x,y = self.position
        min_dist_to_edge = 10
        dist_off_screen = 0

        room_width = self.environment.screen_width
        room_height = self.environment.screen_height

        if x < np.min([min_dist_to_edge, room_width * 0.02]):
            dist_off_screen = np.max([dist_off_screen,
                                      np.abs(np.min([min_dist_to_edge, room_width * 0.02]) - self.position[0])])

        elif x > np.max([room_width - min_dist_to_edge, room_width * .98]):
            dist_off_screen = np.max([dist_off_screen,
                        np.abs(np.max([room_width - min_dist_to_edge, room_width * .98]) \
                        - self.position[0])
                        ])

        elif y < np.min([min_dist_to_edge, room_height * 0.02]):
            dist_off_screen = np.max([dist_off_screen,
                                      np.abs(np.min([min_dist_to_edge, room_height]) - self.position[1])])

        elif y < np.max([room_height - min_dist_to_edge, room_height * .98]):
            dist_off_screen = np.max([dist_off_screen,
                                      np.abs(np.max([room_height - min_dist_to_edge, room_height * .98])
                                      - self.position[1])])

        else:
            dist_off_screen = 0

        attraction_vect = np.array([room_width / 2, room_height / 2]) - self.position
        if np.linalg.norm(attraction_vect) > 0:
            attraction_vect = attraction_vect / np.linalg.norm(attraction_vect)

        return attraction_vect * (dist_off_screen / 10)**2




    def attraction_to_neighbors(self):
        attraction_vect = np.zeros(2)

        for neighbor_wrapper in self.visible_agents[0:np.min([20, len(self.visible_agents)])]:
            neighbor = neighbor_wrapper.animal
            if neighbor is self:
                continue

            difference_in_pos = neighbor.position - self.position
            attraction_vect += difference_in_pos

        if np.linalg.norm(attraction_vect) > 0:
            attraction_vect = attraction_vect / np.linalg.norm(attraction_vect)
            return attraction_vect
        else:
            return attraction_vect

    def repulsion_from_neighbors(self):
        repulsion_vect = np.zeros(2)
        for neighbor in self.visible_agents:
            if neighbor.animal is self:
                continue
            difference_in_pos = self.position - neighbor.animal.position
            dist = np.linalg.norm(difference_in_pos) - (2*Animal.Animal.RADIUS)

            if dist != 0 and dist <= 1:
                repulsion_vect += difference_in_pos / ((dist/100)**2)

        return repulsion_vect

    def repulsion_from_enemies(self):
        repulsion_vect = np.zeros(2)
        for neighbor in self.visible_enemies:
            if neighbor.animal is self:
                continue
            elif neighbor.animal.is_enemy:
                difference_in_pos = self.position - neighbor.animal.position
                dist = np.linalg.norm(difference_in_pos) - Animal.Animal.RADIUS * 2

                if dist != 0 and dist <= self.visible_distance / 2:
                    functional_dist = dist / self.visible_distance
                    repulsion_vect += difference_in_pos / (functional_dist/100) ** 2

        return repulsion_vect

    def orient_with_neighbors(self, dt):
        average_speed = self.coasting_speed

        orient_vector = self.heading()
        rotation_theta = self.turning_tendency + np.random.uniform(low=-np.pi/32, high=np.pi/32) * dt
        rotation_matrix = np.array([[np.cos(rotation_theta), -np.sin(rotation_theta)],
                                    [np.sin(rotation_theta), np.cos(rotation_theta)]])
        orient_vector = rotation_matrix @ orient_vector
        orient_vector = orient_vector * (self.dominance**2)

        for neighbor_wrapper in self.visible_agents[0:np.min([5, len(self.visible_agents)])]:
            neighbor = neighbor_wrapper.animal
            difference_in_pos = self.position - neighbor.position
            dist = np.linalg.norm(difference_in_pos)
            if dist < self.orientation_zone:
                orient_vector += neighbor.heading() * (neighbor.dominance**2) * dt
                average_speed += neighbor.speed

        average_speed = average_speed / (len(self.visible_agents) + 1)
        orient_vector = orient_vector / np.linalg.norm(orient_vector)
        return average_speed, orient_vector

    def attraction_to_grass(self):
        attraction_vect = np.zeros(2)
        for grass in self.visible_grass:
            grass_pos = np.array(grass)
            direction = grass_pos - self.position
            if np.linalg.norm(direction) > 0:
                direction = direction / np.linalg.norm(direction)
            attraction_vect += direction

        if np.linalg.norm(attraction_vect) > 0:
            attraction_vect = attraction_vect / np.linalg.norm(attraction_vect)

        return attraction_vect

    def grass_score(self, grass):
        score = 0
        grass_pos = grass.center()
        grass_size = grass.size

        grass_dist_to_self = np.linalg.norm(np.array(grass_pos) - self.position)
        grass_dist_to_closest_enemy = np.inf

        # if there is a neighbor eating nearby the grass, give it a low score
        for neighbor in self.visible_agents:
            if neighbor.animal.curr_eating is None:
                continue
            dist_to_grass = np.linalg.norm(grass_pos - neighbor.animal.position)
            if dist_to_grass < grass.cell_size / 2:
                return 0

        # calculate the distance from the grass to the nearest enemy to the grass
        for enemy in self.visible_enemies:
            dist = np.linalg.norm(np.array(grass_pos) - enemy.animal.position)
            if dist < grass_dist_to_closest_enemy:
                grass_dist_to_closest_enemy = dist

        # calculate the score
        if grass_dist_to_closest_enemy == np.inf:
            score = (grass_size) * (1 - self.hunger**2) * (self.visible_distance - grass_dist_to_self)
        else:
            score = (grass_size) * \
                    (self.hunger**2) * (self.visible_distance - grass_dist_to_closest_enemy / 2) + \
                    (1 - self.hunger**2) * (self.visible_distance - grass_dist_to_self)

        return score
