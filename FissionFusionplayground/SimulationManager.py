from Environment.Environment import Environment
from Animals.States import DeadState

import numpy as np
from sortedcontainers import SortedList

class AnimalWrapper:
    def __init__(self, animal, distance):
        self.animal = animal
        self.distance = distance

    def __lt__(self, other):
        return self.distance < other.distance

    def __le__(self, other):
        return self.distance <= other.distance

    def __hash__(self):
        return hash((self.animal.visible_distance, self.animal.running_speed, self.distance))

    def __str__(self):
        return str((self.animal, self.distance))


class SimulationManager:
    def __init__(self, sim_width=800, sim_height=600, cell_size=5):
        self.environment = Environment(cell_size=cell_size,
                                       width=int(sim_width / cell_size),
                                       height=int(sim_height / cell_size))

        self.agents = self.environment.animals
        self.enemies = self.environment.enemies
        self.animals = self.enemies + self.agents
        self.grass = self.environment.grass

    def run(self, animate=True):
        if animate:
            self.environment.start_animation()

        running = True
        cycle = 1
        while running:
            if cycle == 0:
                self.update_grass()

            self.update_animals(0.1)
            running = self.environment.update_animation()
            cycle = (cycle + 1) % 300

    def update_grass(self):
        # remove dead_grass
        for grass_key in list(self.grass.keys()):
            if self.grass[grass_key].size == 0:
                self.grass.pop(grass_key)

        for grass_key in list(self.grass.keys()):
            grass = self.grass[grass_key]
            grass.grow()
            #grass.multiply(self.grass)

    def update_animals(self, dt):

        # remove agents that have been eaten
        for agent in self.agents:
            if agent.size == 0:
                self.agents.remove(agent)

        # remove enemies that are dead
        for enemy in self.enemies:
            if enemy.size == 0:
                self.enemies.remove(enemy)

        # calculate which animals are visible to which and which animals can see what grass
        self.animals = self.enemies + self.agents
        self._update_animal_visibilities()
        self._update_agent_grass_visibilities()
        dead_animals = []

        # calculate next state and position, etc. for each animal, agents and enemies
        dt = self.environment.clock.tick(60) / 1000
        for animal in self.agents + self.enemies:
            animal.calc_next(dt)

        # once everything has been calculated, go actually make the updates
        for animal in self.agents + self.enemies:
            if isinstance(animal.state, DeadState.DeadState):
                animal.size = np.max([0, animal.size - 0.001 * dt])

            animal.push_updates()



    def _update_animal_visibilities(self):
        for animal in self.animals:
            animal.visible_enemies = SortedList()
            animal.visible_agents = SortedList()
            if not animal.is_enemy:
                animal.visible_grass = {}

        # for each agent and enemy, build its list of visible enemies and agents
        for i in range(len(self.animals)):
            animal1 = self.animals[i]
            if animal1.is_enemy and isinstance(animal1.state, DeadState.DeadState):       # ignore dead enemies
                continue

            for j in range(i + 1, len(self.animals)):
                animal2 = self.animals[j]
                if animal2.is_enemy and isinstance(animal2.state, DeadState.DeadState):   # ignore dead enemies
                    continue

                # if animal1 can see animal2
                dist = np.linalg.norm(animal1.position - animal2.position)
                if dist < animal1.visible_distance:
                    if animal2.is_enemy:
                        animal1.visible_enemies.add(AnimalWrapper(animal2, dist))

                    else:
                        if animal1.is_enemy or not isinstance(animal2.state, DeadState.DeadState):
                            animal1.visible_agents.add(AnimalWrapper(animal2, dist))

                # if animal2 can see animal1 (The distance they can see may be different)
                if dist < animal2.visible_distance:
                    if animal1.is_enemy:
                        animal2.visible_enemies.add(AnimalWrapper(animal1, dist))

                    else:
                        if animal2.is_enemy or not isinstance(animal1.state, DeadState.DeadState):
                            animal2.visible_agents.add(AnimalWrapper(animal1, dist))

    def _update_agent_grass_visibilities(self):
        grass_positions = np.array(list(self.grass.keys()))
        grass_sizes = np.array([self.grass[tuple(grass_pos)].size for grass_pos in grass_positions])
        probs = grass_sizes / np.sum(grass_sizes)

        num_samples = np.min([len(self.grass), np.max([50, int(np.ceil(len(grass_positions) * 0.08))])])

        # for each animal
        for i in range(len(self.agents)):
            animal = self.agents[i]
            animal.visible_grass = {}
            # grab a random sample of grass (to make it more efficient)
            sample_positions = np.random.choice(len(self.grass), size=num_samples, replace=False, p=probs)
            sample_of_grass = grass_positions[sample_positions]

            # using the sample of grass
            for grass_pos in sample_of_grass:
                grass = self.grass[tuple(grass_pos)]
                grass_center = grass.center()
                dist = np.linalg.norm(grass_center - animal.position)
                if dist < animal.visible_distance:                      # if grass in animal's visible range
                    animal.visible_grass[tuple(grass_center)] = grass
                    score = animal.grass_score(grass)                      # get animal's rating of grass
                    if score > animal.preferred_grass_score and grass.animal is None:
                        # if grass is preferred to animal's current preferred grass
                        animal.preferred_grass_score = score
                        animal.preferred_grass = grass

                    animal.visible_grass[tuple(grass_pos)] = grass              # add to animal's list of visible grass


