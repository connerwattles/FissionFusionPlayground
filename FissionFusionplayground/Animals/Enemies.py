from Animals import Animal
from Animals import Agents
from Animals.States.EnemyStates.HuntState import *
import numpy as np
import heapq


class Enemy(Animal.Animal):
    def __init__(self, environment, x, y, theta):
        Animal.Animal.__init__(self, environment=environment, x=x, y=y, theta=theta,
                               speed=np.random.uniform(low=0, high=5),
                               size=np.random.uniform(low=0.9, high=1),
                               coasting_speed=np.random.uniform(low=5, high=7),
                               running_speed=np.random.uniform(low=18, high=28),
                               standard_acceleration=np.random.uniform(low=8, high=10),
                               max_acceleration=np.random.uniform(low=12, high=24),
                               metabolism=np.random.uniform(low=0.004, high=0.009),
                               fill_rate=np.random.uniform(low=2.4, high=3.4),
                               max_stamina=np.random.uniform(low=2.4, high=3.4),
                               visible_distance=np.random.uniform(low=150, high=200),
                               visible_angle=np.random.uniform(low=7*np.pi/16, high=9*np.pi/16),
                               starting_state=HuntState(self),
                               is_enemy=True)

        self.power = np.max([0.2, 0.4 + 0.1 * np.random.randn()])
        self.acceleration = 0
        # self.dominance = 1 + np.random.exponential(scale=1)
        self.orientation_zone = np.random.uniform(low=30, high=45)
        self.repulsion_to_enemies_zone = np.random.uniform(low=80, high=self.visible_distance)

        self.visible_dead_agents = []


    def calc_next(self, dt):
        self.next_position, self.next_theta, self.next_speed, self.next_state = self.state.transition_logic()


    def attack_target(self, dt):
        if self.curr_target is None:
            return False

        if np.linalg.norm(self.curr_target.position - self.position) < Animal.Animal.RADIUS * 2:
            if not isinstance(self.curr_target.state, DeadState.DeadState):
                self.curr_target.health = np.max([0, self.curr_target.health - self.power * dt])
                self.health = np.max([0, self.health - (self.curr_target.size / 10) * dt])

            return True

        return False


    def attraction_to_prey(self):
        attraction_vect = np.zeros(2)

        prey = [agent.animal for agent in self.visible_agents] \
                    if self.curr_target is None else [self.curr_target]
        for neighbor in prey[0:np.min([1, len(prey)])]:
            if neighbor is self:
                continue

            difference_in_pos = neighbor.position - self.position
            attraction_vect += difference_in_pos

        if np.linalg.norm(attraction_vect) > 0:
            return attraction_vect / np.linalg.norm(attraction_vect)
        else:
            return attraction_vect

    def repulsion_from_enemies(self):
        repulsion_vect = np.zeros(2)
        for neighbor in self.visible_enemies:
            if neighbor.animal is self:
                continue
            difference_in_pos = self.position - neighbor.animal.position
            dist = np.linalg.norm(difference_in_pos) - Animal.Animal.RADIUS * 2

            if dist != 0 and dist <= self.visible_distance:
                repulsion_vect += difference_in_pos / dist ** 2

        return repulsion_vect


    def repulsion_from_agents(self):
        repulsion_vect = np.zeros(2)
        for neighbor in self.visible_agents:
            if neighbor.animal is self:
                continue
            difference_in_pos = self.position - neighbor.animal.position
            dist = np.linalg.norm(difference_in_pos) - (2*Animal.Animal.RADIUS)

            if dist != 0 and dist <= 1:
                repulsion_vect += difference_in_pos / ((dist/100)**2)

        return repulsion_vect

    def attraction_to_neighbors(self):
        attraction_vect = np.zeros(2)

        for neighbor in self.visible_enemies:
            if neighbor.animal.speed > neighbor.animal.coasting_speed:
                p = 1
            else:
                p = 0.3

            if np.random.uniform(low=0, high=1) < p:
                difference = neighbor.animal.position - self.position
                if np.linalg.norm(difference) > 0:
                    difference = difference / np.linalg.norm(difference)
                attraction_vect += difference

        if np.linalg.norm(attraction_vect) > 0:
            attraction_vect = attraction_vect / np.linalg.norm(attraction_vect)

        return attraction_vect
