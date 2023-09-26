import numpy as np
from Animals.States import DeadState
from Animals.States.EnemyStates import EnemyState, HuntState, EnemyWanderingState
from Environment.Grass import Grass


class EnemyEatingState(EnemyState.EnemyState):
    def __init__(self, animal):
        EnemyState.State.__init__(self, animal, "Eating")

    # returns new_pos, new_heading, new_speed, new_state
    def transition_logic(self, dt=0.01):
        self.animal.use_energy(dt)
        if self.animal.curr_eating is None:
            self.animal.curr_eating = self.animal.curr_target

        self.animal.curr_target = None

        next_position = self.animal.position
        next_theta = self.animal.theta
        next_speed = 0
        next_state = self
        if not self.animal.eat_food(dt) or self.animal.hunger >= 1:
            next_state = EnemyWanderingState.EnemyWanderingState(self.animal)
            self.animal.curr_eating = None
        self.animal.update_exhaustion(dt)

        return next_position, next_theta, next_speed, next_state

