from Animals.States.EnemyStates import EnemyState, EnemyEatingState, EnemyWanderingState
from Animals.States.AgentStates import FindFoodState
from Animals.States.AgentStates import WanderingState
from Animals.States import DeadState
from Animals import Animal
import numpy as np


class HuntState(EnemyState.EnemyState):
    def __init__(self, animal):
        EnemyState.State.__init__(self, animal, "Hunt")

    # returns new_pos, new_heading, new_speed, new_state
    def transition_logic(self, dt=0.01):
        self.animal.use_energy(dt)

        if self.animal.health == 0:
            return DeadState.DeadState(self.animal).transition_logic(dt)

        if (self.animal.curr_target is not None) \
                and isinstance(self.animal.curr_target.state, DeadState.DeadState):
            dist = np.linalg.norm(self.animal.position - self.animal.curr_target.position)
            if dist < Animal.Animal.RADIUS * 2.15:
                return self.animal.position, self.animal.theta, 0, EnemyEatingState.EnemyEatingState(self.animal)


        if not self.animal.attack_target(dt):       # if not currently attacking a target
            self.animal.curr_target = self.choose_best_target()

        attraction_to_prey_vect = self.animal.attraction_to_prey()
        repulsion_from_enemies_vect = np.zeros(2)
        if self.animal.is_enemy:
            repulsion_from_enemies_vect = self.animal.repulsion_from_enemies()

        attraction_to_neighbors_vect = self.animal.attraction_to_neighbors()

        self.animal.update_exhaustion(dt)

        if len(self.animal.visible_agents) > 0 and not self.animal.exhausted:
            acceleration = self.animal.max_acceleration
            next_speed = self.animal.running_speed
        else:
            acceleration = self.animal.standard_acceleration
            next_speed = self.animal.coasting_speed

        acceleration_vect =  attraction_to_prey_vect + repulsion_from_enemies_vect

        if self.animal.curr_target is None and len(self.animal.visible_agents) == 0:
            acceleration_vect += attraction_to_neighbors_vect

        if np.linalg.norm(acceleration_vect) > 0:
            acceleration_vect = acceleration_vect / np.linalg.norm(acceleration_vect
                                                                   )
        new_heading = self.animal.heading() + acceleration * acceleration_vect * dt

        new_heading = new_heading / np.linalg.norm(new_heading)

        next_theta = np.arctan2(new_heading[1], new_heading[0])
        next_position = self.animal.position + next_speed * new_heading * dt

        next_state = self

        return next_position, next_theta, next_speed, next_state


    def choose_best_target(self):
        if self.animal.curr_target is not None:
            dist = np.linalg.norm(self.animal.position - self.animal.curr_target.position)
            rand_num = np.random.uniform(low=0, high=1)
            if dist < (3 * Animal.Animal.RADIUS) or rand_num < 0.99:
                return self.animal.curr_target

        if len(self.animal.visible_agents) == 0:
            return None

        # choose te 6 closest agents
        choices = self.animal.visible_agents[0:np.min([6, len(self.animal.visible_agents)])]

        probs = []
        for agent in choices:
            # if spotted a dead animal, have a chance to go eat it instead
            if isinstance(agent.animal.state, DeadState.DeadState):
                rand_num = np.random.uniform(low=0, high=1)
                if rand_num < 0.2:
                    return agent.animal

            probs.append(((1/agent.animal.size) * \
                          np.max([0.1, (1-agent.animal.health + 0.1*np.random.randn())])**2 / \
                          ((agent.distance / self.animal.visible_distance)**2)))


        probs = np.array(probs) / np.sum(probs)
        best = np.random.choice(len(choices), p=probs)
        return choices[best].animal