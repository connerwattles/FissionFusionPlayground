from abc import *
import numpy as np
from sortedcontainers import SortedList


class Animal(ABC):
    RADIUS = 3.9

    def __init__(self, environment, x, y, theta, speed, size, coasting_speed, running_speed,
                 standard_acceleration, max_acceleration, metabolism, fill_rate, max_stamina,
                 visible_distance, visible_angle, starting_state, is_enemy):

        self.environment = environment
        self.is_enemy = is_enemy

        self.position = np.array([x, y])
        self.theta = theta
        self.speed = speed
        self.state = starting_state

        self.health = np.random.uniform(low=0.8, high=1)
        self.stamina = np.random.uniform(low=0.8, high=1) * max_stamina
        self.exhausted = False
        self.hunger = np.min([(np.random.uniform(low=0.5, high=0.8) + 0.01), 1])
        self.size = size

        self.coasting_speed = coasting_speed
        self.running_speed = running_speed
        self.standard_acceleration = standard_acceleration
        self.max_acceleration = max_acceleration
        self.metabolism = metabolism
        self.fill_rate = fill_rate
        self.max_stamina = max_stamina

        self.turning_tendency = np.random.uniform(low=-np.pi/8, high=np.pi/8)

        self.visible_distance = visible_distance
        self.visible_angle = visible_angle

        self.repulsion_to_neighbors_zone = 2 * Animal.RADIUS + 1

        self.visible_agents = SortedList()
        self.visible_enemies = SortedList()

        self.curr_target = None
        self.curr_eating = None

        self.next_position = None
        self.next_theta = None
        self.next_speed = None
        self.next_state = None

    def heading(self):
        return np.array([np.cos(self.theta), np.sin(self.theta)])

    def velocity(self):
        return self.speed * self.heading()

    def new_speed(self, acceleration, dt):
        return np.max([0, np.min([self.max_speed, self.speed + acceleration * dt])])

    def new_pos(self, dt):
        return self.position + self.velocity() * dt

    @abstractmethod
    def calc_next(self, dt):
        pass

    def push_updates(self):
        if self.next_position is not None:
            self.position = self.next_position

        if self.next_theta is not None:
            self.theta = self.next_theta

        if self.next_speed is not None:
            self.speed = self.next_speed

        if self.next_state is not None:
            self.state = self.next_state


        self.next_position = None
        self.next_theta = None
        self.next_speed = None
        self.next_state = None

    def eat_food(self, dt):
        if self.curr_eating is None or self.curr_eating.size == 0 or self.hunger >= 1:
            return False

        amount_leftover = np.max([0, self.curr_eating.size - 0.07 * dt])
        amount_eaten = self.curr_eating.size - amount_leftover
        self.curr_eating.size = amount_leftover

        self.hunger = np.min([1, self.hunger + self.fill_rate * amount_eaten])

        return True

    def use_energy(self, dt):
        self.hunger = np.max([0, self.hunger - (self.metabolism + (self.speed / 500)) * dt])
        if self.hunger <= 0:
            self.health = np.max([0, self.health - 0.03 * dt])
        elif self.hunger > 0.7:
            self.health = np.min([1, self.health + 0.04 * dt])

    def update_exhaustion(self, dt):
        if self.speed <= self.coasting_speed:
            self.stamina = np.min([self.max_stamina, self.stamina + 0.03 * dt])
        else:
            self.stamina = np.max([0, self.stamina - 0.008 * (self.speed - self.coasting_speed) * dt])

        if self.exhausted:
            self.hunger = np.max([0, self.hunger - 0.02 * dt])
            if self.stamina > self.max_stamina * 0.7:
                self.exhausted = False
        else:
            if self.stamina <= 0:
                self.exhausted = True


