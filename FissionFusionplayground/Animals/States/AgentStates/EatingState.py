import numpy as np
from Animals.States.AgentStates import AgentState
from Animals.States.AgentStates import WanderingState
from Animals.States.AgentStates import HerdState
from Animals.States.AgentStates import FindFoodState
from Environment.Grass import Grass


class EatingState(AgentState.State):
    def __init__(self, animal, grass):
        AgentState.State.__init__(self, animal, "Eating")

        self.grass = grass
        self.animal.curr_eating = grass
        self.animal.locked_on_grass = None
        if self.animal in self.grass.locked_on_animals:
            self.grass.locked_on_animals.remove(self.animal)
        self.grass.animal = self.animal

    # returns new_pos, new_heading, new_speed, new_state
    def transition_logic(self, dt=0.01):
        self.animal.use_energy(dt)
        self.animal.update_exhaustion(dt)

        repulsion_from_enemies = self.animal.repulsion_from_enemies()
        if np.linalg.norm(repulsion_from_enemies) > 0:
            self.animal.curr_eating.animal = None
            self.animal.curr_eating = None
            return HerdState.HerdState(self.animal).transition_logic(dt)

        elif self.grass.animal is None:
            self.grass.animal = self.animal

        elif self.animal.curr_eating.animal is not self.animal:
            self.animal.curr_eating = None
            return FindFoodState.FindFoodState(self.animal).transition_logic(dt)

        next_position = self.animal.position
        next_theta = self.animal.theta
        next_speed = 0

        if self.animal.hunger >= 1 or self.grass.size == 0 or self.grass.animal is not self.animal:
            self.animal.curr_eating.animal = None
            self.animal.curr_eating = None
            next_state = HerdState.HerdState(animal=self.animal)

        else:
            next_state = self
            self.animal.eat_food(dt)

        return next_position, next_theta, next_speed, next_state
