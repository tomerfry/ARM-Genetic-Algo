import random
import struct

import unicorn
import capstone


class GeneticModel(object):

    def __init__(self, population, iterations, mutation_probability):
        self.population = population
        self.iterations = iterations
        self.mutation_probability = mutation_probability
        self.fittest_offspring = population

    @staticmethod
    def _evaluate_fitness(sample, wanted_result):
        # Use the Unicorn library to execute the code and measure its performance
        try:
            # Initialize the emulator
            uc = unicorn.Uc(unicorn.UC_ARCH_ARM, unicorn.UC_MODE_ARM)

            # Load the instructions into memory
            uc.mem_map(0x0, 0x1000)
            uc.mem_write(0x0, sample)

            # Set registers to initial values
            uc.reg_write(unicorn.arm_const.UC_ARM_REG_R1, 0)
            uc.reg_write(unicorn.arm_const.UC_ARM_REG_R2, 0)
            uc.reg_write(unicorn.arm_const.UC_ARM_REG_R3, 0)

            # Execute the code
            uc.emu_start(0x0, len(sample))

            # Return the final value of R1 as the fitness score
            result = uc.reg_read(unicorn.arm_const.UC_ARM_REG_R1)

            if result == wanted_result:
                return 1000
            else:
                return 5
        except Exception as e:
            print(str(e))
            return 0

    def run_model(self):
        for generation in range(self.iterations):
            print(f'Generation {generation}:')

            # Evaluate the fitness of each code snippet in the population
            fitness_scores = [self._evaluate_fitness(sample, 10) for sample in self.population]

            # Print the fitness scores
            for code, fitness in zip(self.population, fitness_scores):
                print(f'{code}: {fitness}')

            # Select the fittest code snippets to reproduce
            fittest = [code for _, code in sorted(zip(fitness_scores, self.population))][-5:]
            self.fittest_offspring = fittest[-1]
            # Crossover: combine the fittest code snippets to create new code snippets
            new_population = []
            while len(new_population) < len(self.population):
                parent1 = random.choice(fittest)
                parent2 = random.choice(fittest)
                child = []
                for c1, c2 in zip(parent1, parent2):
                    if random.random() < self.mutation_probability:
                        child.append(~c1 & 0xFF)
                    else:
                        if random.random() < 0.5:
                            child.append(c1)
                new_population.append(bytearray(child))
            self.population = new_population

    def show_fittest_offspring(self):
        cs = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)
        instructions = [i for i in cs.disasm(self.fittest_offspring, 0)]
        for i in instructions:
            print(i)
