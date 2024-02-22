# Written by - Souritra Garai
# Contact - souritra.garai@iitgn.ac.in, sgarai65@gmail.com

# Definition of a class for using Genetic Algorithm
# Uses numpy to optimize iterations and other linear algebra operations
# Make use of Numpy Universal Functions to define the fitness function
# and the fitness vector sorting function

import numpy as np

# definition of class to solve single objective optimization problem
# using particle swarm method
class Genetic_Algorithm :

    def __init__(self) :

        # Dimension of input / no of bytes in each chromosome
        self.__n = None

        # Dimension of Output
        self.__m = None

        # Number of Chromosomes / Population size
        self.__num_chromosomes = None

        # Particles' fitness
        self.__f = None

        # Function to evaluate fitness of chromosomes
        self.__fitness_function = None
    
        # Flag if ready to iterate
        self.__not_ready_2_iterate = True

        # Crossover Probability
        self.__crossover_probability = None

        # Mutation Probability
        self.__mutation_probability = None

        # Function to sort the fitness vector
        self.__sorting_function = None

        # Index to the last chromosome in the Pareto Front
        self.__Pareto_Front_last_index = None

        # Variables keeping track on number of iterations
        # self.__num_chromosomes_iterations = None

    def set_dimensions(self, n, m) :
        ''' Sets the dimension of the search space / no of bytes 
            in each chromosome to n 
            and the dimension of the ouput space to m   '''

        if self.__not_ready_2_iterate == False :

            raise RuntimeError('Running iterations, cannot update now, use stop_iterations() first!!')

        # if type(n)!=int :

        #     raise TypeError('Can accept integer only!!\n')

        # if type(m)!=int :

        #     raise TypeError('Can accept integer only!!\n')

        if n < 1 or m < 1 :

            raise ValueError('At least 1 dimension is required!!\n')

        self.__n = n
        self.__m = m

        pass

    def set_number_of_chromosomes(self, num) :
        ''' Sets the number of chromosomes to be used / population
            size for searching the search space to num   '''

        if self.__not_ready_2_iterate == False :

            raise RuntimeError('Running iterations, cannot update now, use stop_iterations() first!!')

        if type(num)!=int :

            raise TypeError('Can accept integer only!!\n')

        if num < 1 :

            raise ValueError('At least 1 chromosome is required!!\n')

        self.__num_chromosomes = num
        pass

    def set_probabilities(self, crossover_probability, mutation_probability) :
        ''' Sets the probabilities for crossover and mutation   '''

        if self.__not_ready_2_iterate == False :

            raise RuntimeError('Running iterations, cannot update now, use stop_iterations() first!!')

        if type(crossover_probability)!=float :

            raise TypeError('c_p can be float only!!\n')

        if type(mutation_probability)!=float :

            raise TypeError('c_g can be float only!!\n')

        if (np.array([crossover_probability, mutation_probability]) > 1).any() or (np.array([crossover_probability, mutation_probability]) < 0).any() :

            raise ValueError('Probability needs to be in [0, 1]!!')

        self.__crossover_probability = crossover_probability
        self.__mutation_probability = mutation_probability
        pass

    def __init_chromosomes(self) :
        ''' Initialize the particles' position and velocities   '''

        # randomly initializing chromosomes
        self.__chromosomes = np.random.randint(low=0, high=2, size=(self.__num_chromosomes, self.__n), dtype=np.bool)

        pass

    def check_if_initialized(self) :

        variables = ''

        if self.__n == None :

            variables += 'dimension of search space, '

        if self.__num_chromosomes == None :

            variables += 'number of chromosomes to be used, '

        if self.__crossover_probability == None :

            variables += 'crossover probability, '

        if self.__mutation_probability == None :

            variables += 'mutation probability, '

        if self.__fitness_function == None :

            variables += 'function to evaluate fitness, '

        if self.__sorting_function == None :

            variables += 'function to sort fitness vector, '

        if len(variables) > 0 :

            raise RuntimeError(variables[:-2] + ' are not yet initialised!!')

        self.__f = self.__fitness_function(np.zeros((self.__num_chromosomes, self.__n), dtype=np.bool))
        # print(self.__f)
        i, sorted_indices = self.__sorting_function(self.__f, self.__num_chromosomes)
        # print(sorted_indices)
        # print(sorted_indices.shape[0] self.__num_chromosomes)
        # print(sorted_indices.dtype.kind not in np.typecodes['AllInteger'])

        if ( not isinstance(self.__f, np.ndarray) ) or self.__f.shape != (self.__num_chromosomes, self.__m) :

            raise RuntimeError('Fitness Function needs to return numpy array of shape - ' + str((self.__num_chromosomes, self.__m)))

        if ( not isinstance(sorted_indices, np.ndarray) ) or sorted_indices.shape[0] != self.__num_chromosomes or sorted_indices.dtype.kind not in np.typecodes['AllInteger'] :

            raise RuntimeError('Fitness Sorting Function needs to return numpy array of shape - ' + str(tuple(self.__num_chromosomes)) + ' containing int type items')

        if not isinstance(i, np.int) :

            raise RuntimeError('Fitness Sorting Function needs to return an integer as index to the last chromosome in the Pareto front')

        pass

    def set_fitness_function(self, function) :
        ''' Sets the fitness function used to evaluate the 
            vector of fitness values for a chromosome.
            Function should accept entire population of 
            chromosomes as input '''

        if self.__not_ready_2_iterate == False :

            raise RuntimeError('Running iterations, cannot update now, use stop_iterations() first!!')
        
        if not callable(function) :

            raise TypeError('function has to be callable!!\n')

        self.__fitness_function = function
        pass

    def set_sorting_function(self, function) :
        ''' Sets the sorting method used to sort the 
            vectors of fitness values for the chromosomes.
            Function should accept entire population of 
            chromosomes and the as input.
            Function should return tuple of -
            - First, the index to the last chromosome in the Pareto front
            - Second, list of indices for the sorted chromosomes    '''

        if self.__not_ready_2_iterate == False :

            raise RuntimeError('Running iterations, cannot update now, use stop_iterations() first!!')
        
        if not callable(function) :

            raise TypeError('function has to be callable!!\n')

        self.__sorting_function = function
        pass

    def begin(self) :
        ''' Perform the beginning steps of the iterations   '''

        if self.__not_ready_2_iterate == False :

            raise RuntimeError('Running iterations, cannot update now, use stop_iterations() first!!')
        
        # self.check_if_initialized()

        self.__init_chromosomes()

        self.__f = self.__fitness_function(self.__chromosomes)

        self.__Pareto_Front_last_index, sorted_indices = self.__sorting_function(self.__f, self.__num_chromosomes)

        self.__chromosomes = np.copy(self.__chromosomes[sorted_indices])

        self.__f = np.copy(self.__f[sorted_indices])

        self.__not_ready_2_iterate = False
        # self.__num_chromosomes_iterations = 0
        pass

    def iterate(self) :
        ''' Take one step in the iterative process  '''

        if self.__not_ready_2_iterate :

            raise RuntimeError('Not yet ready to iterate, first call begin()!!')

        transition_population = np.vstack((self.__chromosomes, self.__crossover()))

        self.__mutate(transition_population)

        fitness_vector = self.__fitness_function(transition_population)
        
        self.__Pareto_Front_last_index, sorted_indices = self.__sorting_function(fitness_vector, self.__num_chromosomes)

        self.__chromosomes = np.copy(transition_population[sorted_indices])

        self.__f = np.copy(fitness_vector[sorted_indices])
        
        # self.__num_chromosomes_iterations += 1
        pass

    def stop_iterations(self) :
        ''' Let optimizer know that iterations are over.
            You may edit values and restart iterations using begin()    '''

        self.__not_ready_2_iterate = True

        pass

    def __crossover(self) :
        ''' Performs the crossover operation for the chromosome population  '''

        # Make it even
        num_parents = self.__num_chromosomes * self.__crossover_probability - (((self.__num_chromosomes * self.__crossover_probability) % 2 == 1)*1)
        mid_chromosome_index = int(self.__n/2)
        
        parent_indices = np.arange(num_parents, dtype=np.int)
        np.random.shuffle(parent_indices)
        parent_indices = parent_indices.reshape(int(num_parents/2), 2)

        children_1 = np.hstack((self.__chromosomes[parent_indices[:, 0]][:, :mid_chromosome_index], self.__chromosomes[parent_indices[:, 1]][:, mid_chromosome_index:]))
        children_2 = np.hstack((self.__chromosomes[parent_indices[:, 0]][:, :mid_chromosome_index], self.__chromosomes[parent_indices[:, 1]][:, mid_chromosome_index:]))

        return np.vstack((children_1, children_2))

    def __mutate(self, population) :
        ''' Performs random mutations on the given population   '''

        bits_to_mutate = np.random.choice([True, False], size=population.shape, p=[self.__mutation_probability, 1 - self.__mutation_probability])
        np.bitwise_not(population, out=population, where=bits_to_mutate)
        # np.invert()
        pass

    def print_f(self) :

        print(self.get_Pareto_Front_fitness_values(), self.get_Pareto_Front_chromosomes())

        pass

    def get_Pareto_Front_chromosomes(self) :
        ''' Returns the chromosomes in the Pareto front '''

        return np.copy(self.__chromosomes[:self.__Pareto_Front_last_index + 1])

    def get_Pareto_Front_fitness_values(self) :
        ''' Returns the fitness values of the chromosomes in the Pareto front   '''

        return np.copy(self.__f[:self.__Pareto_Front_last_index])

    def get_non_Pareto_Front_fitness_values(self) :

        return np.copy(self.__f[self.__Pareto_Front_last_index:])

if __name__ == "__main__":
    
    def func(matrix) :

        # n = matrix.shape[0]

        vector = np.packbits(matrix, axis=1)

        return np.tan( vector * np.pi / (255*2))

    def my_sort(vector, num) :

        # print(np.argsort(vector[:, 0])[-num:])
        # print(num)

        return 0, np.argsort(vector[:, 0])[-num:]
    
    problem = Genetic_Algorithm()
    
    problem.set_dimensions(8, 1)
    problem.set_number_of_chromosomes(100)
    problem.set_probabilities(0.5, 0.005)
    problem.set_fitness_function(func)
    problem.set_sorting_function(my_sort)

    problem.begin()

    problem.print_f()
    
    for i in range(100) :
        
        problem.iterate()
        problem.print_f()
    
    problem.stop_iterations()
