import random
import os
from copy import deepcopy


class Individual(object):
    def __init__(self, o):
        self.o = o
        self.fitness = None
        self.characteristics = None

    def clone(self):
        c = Individual(deepcopy(self.o))

        return c

    def __str__(self):
        return str(self.o)

class MAPElites(object):
    def __init__(self, dims, solution_generator, mutate, initial_population=10, evaluator=None, batch_evaluator=None):
        self._dims = dims
        self._solution_generator = solution_generator
        self._mutate = mutate
        self._evaluator = evaluator
        self._batch_evaluator = batch_evaluator
        self._initial_population = initial_population

        self._log_folder = "map_elites_checkpoints"
        if not os.path.exists(self._log_folder):
            print "Creating logfolder"
            os.makedirs(self._log_folder)
        
        self._pop = None
        
    def __getstate__(self):
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state['_solution_generator']
        del state['_evaluator']
        del state['_batch_evaluator']
        del state['_mutate']
        return state

    def _recursive_matrix_helper(self, base, dims):
        dim = dims[0]
        
        for i in range(dim):
            base.append([]) 
        
        if len(dims) > 1:   
            return [self._recursive_matrix_helper(cell, dims[1:]) for cell in base]
        else:
            return base
            
    def _create_pop(self):
        pop = self._recursive_matrix_helper([], self._dims)
        return pop
        
    def init(self):
        self._pop = self._create_pop()
        
        individual_batch = [Individual(self._solution_generator()) for i in range(self._initial_population)]
        
        if self._batch_evaluator is not None:

            solutions = map(lambda i: i.o, individual_batch)
            results = self._batch_evaluator(0,  solutions)
            

            for individual, (fitness, characteristics) in zip(individual_batch, results):
                individual.characteristics = characteristics
                individual.fitness = fitness
        else:
            for individual in individual_batch:
                fitness, characteristics = self._evaluator(0, individual.o)
                individual.characteristics = characteristics
                individual.fitness = fitness

        map(self._place_solution, individual_batch)
        
        return self 
        
    def __exit__(self, type, value, traceback):
        pass
        
    def _random_indexes(self):
        return [random.randint(0, dim-1) for dim in self._dims]
        
    def _get_individual(self, indexes):
        copy_indexes = indexes[:]
        r = self._pop
        while len(copy_indexes) > 0:
            r = r[copy_indexes.pop(0)]
            
        if len(r) == 0:
            return None
        else:
            return r[0]

    def save_checkpoint(self, filename=None):
        if filename is None:
            filename = "mapelites_default.chkpt"

        import cPickle

        f = open(filename, "w")
        cPickle.dump(self, f)
        f.close()
        
    def _place_solution(self, solution):
        characteristic_values = list(solution.characteristics.values())

        assert len(characteristic_values) == len(self._dims), "Wrong number of characteristics valued returned by fitness (%s)" % str( solution.characteristics )

        indexes = []
        for i, v in enumerate(characteristic_values):            
            steps = 1./(self._dims[i]-1)

            # Fix for this issue, add 0.00001
            # Python 2.7.12 (default, Nov 19 2016, 06:48:10) 
            # [GCC 5.4.0 20160609] on linux2
            # >>> int(0.3/0.1)
            # 2
            # >>> 0.1/0.1
            # 1.0
            # >>> 0.2/0.1
            # 2.0
            # >>> 0.3/0.1
            # 2.9999999999999996
            # >>> 0.4/0.1
            # 4.0
            # >>> 0.5/0.1
            # 5.0
            # >>> 0.6/0.1
            # 5.999999999999999
            bin_index = max(0, min(self._dims[i]-1, int(characteristic_values[i]/steps+0.00001)))



            indexes.append(bin_index)

        r = self._pop
        while len(indexes) > 0:
            r = r[indexes.pop(0)]
            
        if len(r) == 0:
            r.append(solution)
        else:            
            if solution.fitness > r[0].fitness:
                r.pop()
                r.append(solution)

    def _get_random_individual(self, on_boarder=False):

        indexes = self._random_indexes()
        ind = self._get_individual(indexes)

        retry_count = 10
        connections = 1
        while ind is None or (on_boarder and self._neighbour_count(indexes) > connections):

            if retry_count == 0:
                connections += 1
                retry_count = 10

            retry_count -= 1

            #print ind, self._neighbour_count(indexes)

            indexes = self._random_indexes()
            ind = self._get_individual(indexes)
        return ind

    #Guaranteed to return indexes to a valid individual (if the MAP contains one)
    def _random_valid_indexes(self):
        indexes = [random.randint(0, dim-1) for dim in self._dims]

        while self._get_individual(indexes) is None:
            indexes = [random.randint(0, dim-1) for dim in self._dims]

        return indexes

    #
    def _border_tournament_indexes(self, n=5):
        list_of_indexes = [self._random_valid_indexes() for _ in range(n)]


        return min(list_of_indexes, key=self._neighbour_count)

    def _neighbour_count(self, indexes):
        count = 0

        for i in range(len(indexes)):
            copy_indexes = indexes[:]

            copy_indexes[i] = copy_indexes[i] + 1
            if self._dims[i] == copy_indexes[i]: 
                count += 1
            elif self._get_individual(copy_indexes) is not None :
                count += 1

            copy_indexes[i] = copy_indexes[i] - 2
            if copy_indexes[i] == 0:
                count += 1

            elif self._get_individual(copy_indexes) is not None:
                count += 1

        return count


    def run_batch(self, n_gen = 1000, batch_size = 10, prefer_border=False):
        for gen in range(1,n_gen):

            checkpoint_name = os.path.join(self._log_folder,"mapelites_gen_%s.chkpt" % gen)
            self.save_checkpoint(checkpoint_name)

            individual_batch = []

            for n in range(batch_size):

                if prefer_border and False:
                    indexes = self._border_tournament_indexes()
                    offspring = self._get_individual(indexes)
                else:
                    offspring = self._get_random_individual(prefer_border).clone()
                offspring.o = self._mutate(offspring.o)
                individual_batch.append(offspring)



            if self._batch_evaluator is not None:

                solutions = map(lambda i: i.o, individual_batch)
                results = self._batch_evaluator(gen, solutions)
                

                for individual, (fitness, characteristics) in zip(individual_batch, results):
                    individual.characteristics = characteristics
                    individual.fitness = fitness
            else:
                for individual in individual_batch:
                    fitness, characteristics = self._evaluator(gen, individual.o)
                    individual.characteristics = characteristics
                    individual.fitness = fitness

            for individual in individual_batch:
                self._place_solution(individual)

    
    def _get_sub_matrix(self, i ):
        return self._pop[i]
        
    def _extract_fitness_2dmatrix(self, sub_matrix):
        r = []
        
        for i in range(len(sub_matrix)):
            row = []
            for j in range(len(sub_matrix[0])):
                if len(sub_matrix[i][j]) == 1:
                    row.append(sub_matrix[i][j][0].fitness)
                else:
                    row.append(-1.0)
                
            r.append(row)
            
        return r
    
    def get_plottable_fitness(self):
        evaluated_matrix = self._extract_fitness_2dmatrix(self._pop)
        return evaluated_matrix

    def get_individuals(self, indexes, depth=0, root=None):

        assert depth + len(indexes) == len(self._dims)

        if root is None:
            root = self._pop

        i = indexes.pop(0)

        if i is None:
            if len(indexes) == 0:
                return root
            else:
                r = []
                for c in root:
                    t = self.get_individuals(indexes[:], depth+1, root=c)
                    r.append(t)

                return r
        else:
            if len(indexes) == 0:
                return root[i]
            else:
                return self.get_individuals(indexes[:], depth+1, root=root[i])
        
    def _recursive_get(self, base, current_indicies=[]):
        if len(base) == 0:
            return []
        elif len(base) == 1:
            return [tuple(current_indicies + [base[0]])]
        else:
            r = []
            [r.extend(self._recursive_get(sub_base, current_indicies + [i])) for i,sub_base in enumerate(base)]
            return r
        
    def get_all_solutions(self):
        solutions = self._recursive_get(self._pop)
        return solutions
    
    def __len__(self):
        return len(self.get_all_solutions())
        
