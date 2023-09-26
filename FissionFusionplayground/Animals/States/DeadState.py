import numpy as np
from Animals.States import State
from Animals.States.AgentStates import AgentState
from Animals.States.AgentStates import WanderingState
from Animals.States.AgentStates import HerdState
from Animals.States.AgentStates import FindFoodState
from Environment.Grass import Grass


class DeadState(AgentState.AgentState):
    def __init__(self, animal):
        AgentState.AgentState.__init__(self, animal, "Dead")
        self.turns_dead = 0

    # returns new_pos, new_heading, new_speed, new_state
    def transition_logic(self, dt=0.01):
        self.turns_dead += dt
        next_position = self.animal.position
        next_theta = self.animal.theta
        next_speed = 0
        next_state = self

        if not self.animal.is_enemy:
            if self.animal.curr_eating is not None:
                self.animal.curr_eating.animal = None
                self.animal.curr_eating = None

            if self.animal.locked_on_grass is not None:
                self.animal.locked_on_grass.locked_on_animals.remove(self.animal)
                self.animal.locked_on_grass = None

        return next_position, next_theta, next_speed, next_state
