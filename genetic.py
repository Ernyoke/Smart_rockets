from rocket import Rocket, Vector, Obstacle
import numpy as np
import pygame

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

FPS = 60


class Genetic:

    def __init__(self, loc_x, loc_y, population_size=50, mutation_rate=0.1, obstacles=[]):
        # initialize all variables
        self.target_location = Vector(loc_x, loc_y)
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.population = []
        self.best_child = Rocket(FPS)
        self.obstacles = []

        # initialize the rockets at random values
        for i in range(0, self.population_size):
            self.population.append(Rocket(FPS))

        # create obstacle objects
        for obs in obstacles:
            self.obstacles.append(Obstacle(obs[0], obs[1], obs[2], obs[3]))

    # implementation of the genetic algorithm
    def _next_gen(self):

        # define aux variables for genetic algirthm
        mating_pool = []
        new_generation = []

        for member in self.population:

            # calculate the fitness for every member from the population
            fitness = (member.fitness(self.target_location)) * 1000

            # save the member with the best fitness
            if self.best_child.fitness(self.target_location) * 1000 < fitness:
                self.best_child = member

            # create the mating pool using every member's fitness
            # the recombination will use roulette method which means every member
            # is added to the mating pool multiple times depending on its fitness value
            for i in range(0, int(fitness)):
                mating_pool.append(member)

        for i in range(0, self.population_size):

            # the recombination is done selecting to random members from the mating pool
            first = np.random.random_integers(0, len(mating_pool) - 1)
            second = np.random.random_integers(0, len(mating_pool) - 1)
            child = mating_pool[first].crossover(mating_pool[second])

            # the child will suffer a mutation according to the probability of the mutation rate
            child.mutate(self.mutation_rate)

            # the newer generation will represent the population for the next iteration
            new_generation.append(child)

        self.population = new_generation

    # this method computes the routes of the rockets without using visual simulation
    def simulate(self, iterations):
        for i in range(0, iterations):

            # apply all forces for every member
            for member in self.population:
                for force in member.forces:

                    # do not update the rockets position if it did collide with an obstacle
                    if member.is_alive:

                        # apply force to the rocket
                        member.apply_force(force)

                        # update rocket's position
                        member.update()

                        # check member's collision with the obstacles
                        for obs in self.obstacles:
                            if obs.do_collide(member):
                                member.is_alive = False

            # compute the newer generation
            self._next_gen()

    # this method computes the routes of the rockets using visual simulation
    def simulate_with_graphics(self, title="Rockets", width=800, height=600):

        # calculate an offset point to be able to draw negative positions
        reference_point = Vector(width / 4, height / 4)

        # initialize pygame
        pygame.init()
        game_display = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)

        # get the clock module for handling FPS
        clock = pygame.time.Clock()

        # set an exit flag
        game_exit = False

        # set a counter for handling genetic algorithm steps at given moments
        counter = 0

        # iteration counter
        gen_iter = 0

        # start the main loop
        while not game_exit:

            # handle input events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_exit = True

            # clear the playground
            game_display.fill(BLACK)

            if counter == FPS:

                # reset the counter to 0
                counter = 0

                # increment iter
                gen_iter += 1

                # compute the newer generation of the population
                self._next_gen()

            for member in self.population:

                # check if rocket did not collide before
                if member.is_alive:

                    # calculate the new position for every rocket
                    member.apply_force_at(counter)

                    # update the rocket's position
                    member.update()

                    # check member's collision with the obstacles
                    for obs in self.obstacles:
                        if obs.do_collide(member):
                            member.is_alive = False

                # display the rockets
                pygame.draw.circle(game_display, WHITE, member.location.tuple_int(reference_point.x), 1)

            counter += 1

            # display the target position
            pygame.draw.circle(game_display, RED, self.target_location.tuple_int(reference_point.x), 3)

            # draw the obstacles
            for obs in self.obstacles:
                rect = obs.tuple_int(reference_point.x)
                pygame.draw.rect(game_display, WHITE, (rect[0],
                                                       (rect[1][0] - rect[0][0], rect[1][1] - rect[0][1])))

            # display iteration number to the screen
            font = pygame.font.SysFont("monospace", 15)
            label = font.render("iteration: " + str(gen_iter), 1, (255, 255, 0))
            game_display.blit(label, (width - 150, 10))

            # update the display
            pygame.display.update()

            # sleep the mainloop for achieving the preset FPS value
            clock.tick(FPS)
