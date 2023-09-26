from Animals.States.AgentStates import AgentState, HerdState, FindFoodState


class WanderingState(AgentState.AgentState):
    def __init__(self, animal):
        AgentState.AgentState.__init__(self, animal, "Wander")

    # returns new_pos, new_heading, new_speed, new_state
    def transition_logic(self, dt=0.01):
        return HerdState.HerdState(self.animal).transition_logic(dt)

        # # update state
        # if self.animal.hunger < 0.4 and len(self.animal.visible_grass) > 0:
        #     new_state = FindFoodState.FindFoodState(animal=self.animal)
        # elif len(self.animal.visible_neighbors) > 0:
        #     new_state = HerdState.HerdState(animal=self.animal)
        # else:
        #     new_state = self
        #
        # # update animal's hunger bar
        # self.animal.update_hunger(dt)
        #
        # return new_pos, new_heading, new_speed, new_state
