from Animals.States.AgentStates import AgentState, EatingState, FindFoodState, WanderingState
from Animals.States import DeadState
import numpy as np


class HerdState(AgentState.AgentState):
    def __init__(self, animal):
        AgentState.State.__init__(self, animal, "Herd")

    # returns new_pos, new_heading, new_speed, new_state
    def transition_logic(self, dt=0.01):

        if self.animal.health == 0:
            return DeadState.DeadState(self.animal).transition_logic(dt)

        attraction_to_neighbors_vect = self.animal.attraction_to_neighbors()
        attraction_to_center_vect = self.animal.attraction_to_center()
        attraction_to_grass_vect = self.animal.attraction_to_grass()
        repulsion_from_neighbors_vect = self.animal.repulsion_from_neighbors()

        repulsion_from_enemies_vect = np.zeros(2)
        if not self.animal.is_enemy:
            repulsion_from_enemies_vect = self.animal.repulsion_from_enemies()

        average_neighbor_speed, orientation_vect = self.animal.orient_with_neighbors(dt)

        self.animal.update_exhaustion(dt)

        if self.animal.curr_eating is not None:
            self.animal.curr_eating.animal = None
            self.animal.curr_eating = None

        if self.animal.locked_on_grass is not None:
            self.animal.locked_on_grass.locked_on_animals.remove(self.animal)
            self.animal.locked_on_grass = None

        if len(self.animal.visible_enemies) > 0 and not self.animal.exhausted:
            acceleration = self.animal.max_acceleration
            next_speed = self.animal.running_speed
        else:
            acceleration = self.animal.standard_acceleration
            next_speed = average_neighbor_speed
            if next_speed < self.animal.coasting_speed:
                next_speed = self.animal.coasting_speed

        acceleration_vector = attraction_to_neighbors_vect + repulsion_from_neighbors_vect + \
            repulsion_from_enemies_vect + orientation_vect + attraction_to_center_vect + attraction_to_grass_vect

        if np.linalg.norm(acceleration_vector) > 0:
            acceleration_vector = acceleration_vector / np.linalg.norm(acceleration_vector)

        new_heading = self.animal.heading() + (acceleration * acceleration_vector * dt)
        new_heading = new_heading / np.linalg.norm(new_heading)

        next_theta = np.arctan2(new_heading[1], new_heading[0])
        next_position = self.animal.position + new_heading * next_speed * dt

        next_state = self
        if np.linalg.norm(repulsion_from_enemies_vect) == 0 and self.animal.hunger < 0.6:
            next_state = FindFoodState.FindFoodState(self.animal)

        return next_position, next_theta, next_speed, next_state
