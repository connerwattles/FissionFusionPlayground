from Animals.States.EnemyStates import HuntState, EnemyState
from Animals.States import DeadState
import numpy as np


class EnemyWanderingState(EnemyState.EnemyState):
    def __init__(self, animal):
        EnemyState.EnemyState.__init__(self, animal, "Wander")

    # returns new_pos, new_heading, new_speed, new_state
    def transition_logic(self, dt=0.01):
        self.animal.use_energy(dt)
        if self.animal.health == 0:
            return DeadState.DeadState(self.animal).transition_logic(dt)

        self.animal.curr_target = None

        amount_to_turn = self.animal.turning_tendency + 0.1 * np.random.randn()
        turning_vector = np.array([np.cos(amount_to_turn),
                                   np.sin(amount_to_turn)])
        new_heading = self.animal.heading() + turning_vector * dt
        new_heading += self.animal.standard_acceleration * \
                         (self.animal.repulsion_from_agents() +
                          self.animal.repulsion_from_enemies() +
                          self.animal.attraction_to_neighbors() +
                          self.animal.attraction_to_prey() / 3) * dt

        if np.linalg.norm(new_heading) > 0:
            new_heading = new_heading / np.linalg.norm(new_heading)

        next_speed = self.animal.coasting_speed

        next_theta = np.arctan2(new_heading[1], new_heading[0])
        next_position = self.animal.position + new_heading * next_speed * dt

        # update state
        if self.animal.hunger < 0.6:
            next_state = HuntState.HuntState(animal=self.animal)
        else:
            next_state = self

        self.animal.update_exhaustion(dt)

        return next_position, next_theta, next_speed, next_state
