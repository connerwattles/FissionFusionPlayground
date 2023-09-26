import numpy as np

class Grass:
    def __init__(self, pos, cell_size, size=None):
        self.x, self.y = pos
        self.size = ((np.random.uniform(low=0, high=1) + 0.01) % 1) if size is None else size
        self.cell_size = cell_size

        self.locked_on_animals = []
        self.animal = None

    def pos(self):
        return np.array([self.x, self.y])

    def center(self):
        return np.array([self.x, self.y]) + self.cell_size / 2

    def grow(self):
        if self.animal is not None:
            return

        self.size = np.min([(self.size + 0.02), 1])

    def multiply(self, all_grass):
        if self.animal is not None:
            return

        rand = np.random.uniform(low=0, high=1)
        if rand < self.size:
            for neighbor in [[1, 0], [0, 1], [0, -1], [-1, 0]]:
                rand2 = np.random.uniform(low=0, high=1)
                if rand2 < 0.5:
                    child_pos = list(self.pos() + self.cell_size * np.array(neighbor))
                    child_pos[0] = int(child_pos[0])
                    child_pos[1] = int(child_pos[1])
                    child_pos = tuple(child_pos)

                    if child_pos in all_grass.keys():
                        pass
                    else:
                        all_grass[child_pos] = Grass(pos=self.pos() + self.cell_size * np.array(neighbor),
                                                     cell_size = self.cell_size,
                                                     size=0.05)
    def set_animal(self, animal):
        self.animal = animal

    def clear_animal(self):
        self.animal = None

    def __hash__(self):
        return hash((self.x, self.y))