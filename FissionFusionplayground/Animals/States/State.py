from abc import *
from Animals.Animal import *
import numpy as np


class State(ABC):
    def __init__(self, animal, name):
        ABC.__init__(self)
        self.animal = animal
        self.name = name

    @abstractmethod
    def transition_logic(self, dt):
        """
        Should use information about the agent position and current state to return both the
        new position of the agent and the new state of the agent. If the state is the same,
        then the method should return self as the new state with the num_iters_in_Sstate
        incremented by 1

        Return new_state, new_pos
        """
        pass

    def repulsion_to_agents_vector(self):
        repulsion_vect = np.zeros(2)
        for neighbor in self.animal.visible_agents:
            if neighbor is self:
                continue
            difference_in_pos = self.animal.position - neighbor.position
            dist = np.linalg.norm(difference_in_pos) - 2*Animal.RADIUS

            if dist != 0 and dist <= 1:
                repulsion_vect += difference_in_pos / dist**2

        return repulsion_vect

    def random_walk(self, dt):
        new_speed = self.animal.coasting_speed

        turning_angle = (self.animal.turning_inclination + np.random.uniform(low=-0.2, high=0.2)) * dt
        rotation_matrix = np.array([[np.cos(turning_angle), -np.sin(turning_angle)],
                                    [np.sin(turning_angle),  np.cos(turning_angle)]])
        new_heading = rotation_matrix @ self.animal.heading()

        new_pos = self.animal.pos() + (self.animal.heading() * (self.animal.speed * dt))

        return new_pos, new_heading, new_speed

    def __str__(self):
        return self.name




