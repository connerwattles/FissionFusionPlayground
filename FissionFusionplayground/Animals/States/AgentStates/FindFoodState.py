from Animals.States.AgentStates import AgentState
from Animals.States.AgentStates import EatingState, WanderingState, HerdState
from Animals.States import DeadState
import numpy as np


class FindFoodState(AgentState.AgentState):
    def __init__(self, animal):
        AgentState.State.__init__(self, animal, "Find Food")
        self.wandering = None
        self.turns_on_empty = 0

    # returns new_pos, new_heading, new_speed, new_state
    def transition_logic(self, dt=0.01):
        self.animal.use_energy(dt)

        if self.animal.health == 0:
            return DeadState.DeadState(self.animal).transition_logic(dt)


        self.animal.update_exhaustion(dt)

        repulsion_from_enemies = self.animal.repulsion_from_enemies()

        if np.linalg.norm(repulsion_from_enemies) > 0:
            return HerdState.HerdState(self.animal).transition_logic(dt)

        # if preferred grass is better, then with 20% chance go there
        if self.animal.locked_on_grass is None:
            if self.animal.preferred_grass is not None:
                self.animal.locked_on_grass = self.animal.preferred_grass
                self.animal.locked_on_grass_score = self.animal.preferred_grass_score
                self.animal.locked_on_grass.locked_on_animals.append(self.animal)

        elif self.animal.locked_on_grass.animal is not self.animal:
            self.animal.locked_on_grass.locked_on_animals.remove(self.animal)
            self.animal.locked_on_grass = None
            self.animal.locked_on_grass_score = -np.inf

            if self.animal.preferred_grass is not None:
                self.animal.locked_on_grass = self.animal.preferred_grass
                self.animal.locked_on_grass_score = self.animal.preferred_grass_score
                self.animal.locked_on_grass.locked_on_animals.append(self.animal)

        elif self.animal.preferred_grass_score > self.animal.locked_on_grass_score:
            rand_num = np.random.uniform(low=0, high=1)
            if rand_num < 0.05 * dt:
                self.animal.locked_on_grass.locked_on_animals.remove(self.animal)
                self.animal.locked_on_grass = self.animal.preferred_grass
                self.animal.locked_on_grass_score = self.animal.preferred_grass_score
                self.animal.locked_on_grass.locked_on_animals.append(self.animal)


        if self.animal.locked_on_grass is None:
            next_position, next_theta, next_speed, next_state = WanderingState.WanderingState(self.animal).transition_logic(dt)
            return next_position, next_theta, next_speed, self

        # if animal is close enough to its locked on grass and no other animal is eating it, start eating it
        elif np.linalg.norm(self.animal.position - self.animal.locked_on_grass.pos()) < (self.animal.speed * dt + 3):   # if animal close enough to the grass its pursuing
            next_speed = 0
            next_theta = self.animal.theta
            next_position = self.animal.position
            next_state = EatingState.EatingState(animal=self.animal, grass=self.animal.locked_on_grass)

        else:

            direction_to_grass = self.animal.locked_on_grass.pos() - self.animal.position
            if np.linalg.norm(direction_to_grass) > 0:
                direction_to_grass = direction_to_grass / np.linalg.norm(direction_to_grass)
            attraction_to_neighbors = self.animal.attraction_to_neighbors()
            repulsion_from_neighbors = self.animal.repulsion_from_neighbors()
            repulsion_from_enemies = self.animal.repulsion_from_enemies()

            acceleration_vector = 2 * (1 - self.animal.hunger**2) * direction_to_grass + \
                                  (self.animal.hunger**2) * attraction_to_neighbors + \
                                  repulsion_from_neighbors

            if np.linalg.norm(acceleration_vector) > 0:
                acceleration_vector = acceleration_vector / np.linalg.norm(acceleration_vector)

            acceleration = self.animal.standard_acceleration
            next_speed = self.animal.coasting_speed

            new_heading = self.animal.heading() + (acceleration * acceleration_vector * dt)
            new_heading = new_heading / np.linalg.norm(new_heading)

            next_theta = np.arctan2(new_heading[1], new_heading[0])
            next_position = self.animal.position + new_heading * next_speed * dt

            next_state = self

        return next_position, next_theta, next_speed, next_state

