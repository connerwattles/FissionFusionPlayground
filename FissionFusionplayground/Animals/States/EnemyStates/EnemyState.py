from Animals.States.State import *
from Animals import Animal
from Animals import Agents
from Animals import Enemies
from abc import *
import numpy as np


class EnemyState(State, ABC):

    def __init__(self, agent, name):
        ABC.__init__(self)
        State.__init__(self, agent, name)

    @abstractmethod
    def transition_logic(self, dt):
        pass
