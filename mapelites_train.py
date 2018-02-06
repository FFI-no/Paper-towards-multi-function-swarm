
from map_elites import MAPElites

from simulator import run_simulations_serial, run_simulations_parallel

from case_generator.random_cases import RandomCases
from case_generator.localization_cases import LocalizationCases
from case_generator.base_connectivity import BaseConnectivity
from case_generator.network_cases import NetworkCases
from case_generator.exploration_cases import ExplorationCases
from case_generator.combined_cases import CombinedCases

import random
from fitness_evaluator import Evaluator
import copy
import argparse
import sys
import numpy as np

class Genome(object):
    def __init__(self, size=4):
        self._size = size
        #init random

        self._weights = (np.random.rand(size)*2.-np.ones(size))*100.
        self._centers = np.random.rand(size)*900.+np.ones(size)*100.
        self._spreads = np.random.rand(size)*100.
        self._scales = (np.random.rand(size)*2.-np.ones(size))

    def clone(self):
        i = Genome()

        i._weights = self._weights
        i._centers = self._centers
        i._spread = self._spreads
        i._scale = self._scales

    def mutate(self):
        mutated = False
        while not mutated:
            i = random.randint(0, self._size*4-1)

            li = i%self._size

            if i < self._size:   
                #mutate weights
                self._weights[li] += random.gauss(0., 10.)
                self._weights[li] = max(-100., min(100., self._weights[li])) 

            elif self._size < i < self._size*2:
                #mutate centers
                self._centers[li] += random.gauss(0., 100.)
                self._centers[li] = max(100., min(1000., self._centers[li])) 

            elif 3*self._size < i < 4*self._size:
                #mutate spread
                self._spreads[li] += random.gauss(0., 10.)
                self._spreads[li] = max(0., min(100., self._spreads[li])) 

            else:
                #mutate scale
                self._scales[li] += random.gauss(0., 0.1)
                self._scales[li] = max(-1., min(1., self._scales[li])) 

            mutated=True
            
    def __str__(self):
        import json

        t = {"weights": list(self._weights), "centers": list(self._centers), "spreads": list(self._spreads), "scales": list(self._scales)}
        return json.dumps(t)


def main(visualize, parallel, cont_type, test_mode=False):
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.colors import ListedColormap
    from mpl_toolkits.mplot3d import Axes3D

    if test_mode:
        print >>sys.stderr, "*****TEST MODE ENABLED*****"
    
    if test_mode:
        dims = [11,101]
    else:
        dims = [11,101]

    solution_size = 4

    gi = 0

    seed = random.randint(0,1000000)

    f = open("seed.txt","w")
    f.write(str(seed))
    f.close()

    random.seed(seed)

    def batch_evaluator(epoch, solutions):        
        if test_mode:

            case_configs = []
            case_configs.extend(CombinedCases([1000.0,1000.0],5,20))
        else:
            case_configs = []
            case_configs.extend(CombinedCases([1000.0,1000.0],5,20))

        if cont_type =="weighted":
            eva = Evaluator()
        elif cont_type=="parametric": 
            eva = Evaluator(parametric=True)

        solutions_caseconfigs = []

        for si, solution in enumerate(solutions):

            #Push each simulation to a compute node
            # Inputs: Controller, Cases
            # Outputs: Fitness
            
            new_case_configs = []
            for case_config in case_configs:
                config_copy = copy.deepcopy(case_config)
                for platform_type in config_copy["platform_templates"].keys():
                    if cont_type == "weighted":
                        config_copy["platform_templates"][platform_type]["behavior"] = "MAPElitesWeighted"
                        config_copy["platform_templates"][platform_type]["config_behavior"] = {"interval": 0.5,"weights": solution}
                    elif cont_type == "parametric":
                        config_copy["platform_templates"][platform_type]["behavior"] = "MAPElitesParametric"
                        config_copy["platform_templates"][platform_type]["config_behavior"] = {}
                        config_copy["platform_templates"][platform_type]["config_behavior"]["interval"] = 0.5
                        config_copy["platform_templates"][platform_type]["config_behavior"]["weights"] = solution._weights
                        config_copy["platform_templates"][platform_type]["config_behavior"]["center"] = solution._centers
                        config_copy["platform_templates"][platform_type]["config_behavior"]["spread"] = solution._spreads
                        config_copy["platform_templates"][platform_type]["config_behavior"]["scale"] = solution._scales
                    else:
                        raise Exception("No such controller type (%s)" % cont_type)

                config_copy['epoch'] = epoch
                config_copy['individual'] = si


                config_copy["config_simulator"] = {"max_time": 900.0, "view_delay": 6.0, "log_delay": 200.0, "grid_size": [1000.0, 1000.0]}

                if test_mode:
                    config_copy["config_simulator"]["max_time"] = 10.
                    config_copy["config_simulator"]["log_delay"] = 1.0
                else:
                    config_copy["config_simulator"]["max_time"] = 900.
                    config_copy["config_simulator"]["log_delay"] = 100.0

                new_case_configs.append(config_copy)

            solutions_caseconfigs.append((solution, new_case_configs))

        if parallel:
            solution_logs = run_simulations_parallel(solutions_caseconfigs)#, False)
        else: 
            solution_logs = run_simulations_serial(solutions_caseconfigs, visualize)

        solutions_results = []
        for solution, logs in solution_logs:
            fitness, characteristics = eva.fitness_map_elites(logs)

            solutions_results.append((fitness, characteristics))

        import shutil
        shutil.rmtree("logs")
            
        return solutions_results

    if cont_type=="weighted":
        def mutate(solution):
            i = random.randint(0, solution_size-1)
            solution[i] += random.gauss(0., 10.)
            solution[i] = max(-100., min(100., solution[i])) 
            
            return solution
        
        def generate():
            return np.random.rand(solution_size)*200.-np.ones(solution_size)*100.

    elif cont_type=="parametric":
        def mutate(solution):
            solution.mutate()
            return solution
        
        def generate():
            return Genome()
    else: 
        raise Exception("No such controller (%s)" % cont_type)

    if test_mode:
        m = MAPElites(dims, generate, mutate, 2, batch_evaluator=batch_evaluator) 
    else:
        m = MAPElites(dims, generate, mutate, 200, batch_evaluator=batch_evaluator) 
    m.init()

    if test_mode:
        m.run_batch(4,1)
    else:
        m.run_batch(201,200)
 

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--parallel', dest='parallel', action='store_true')
    parser.set_defaults(parallel=False)
    parser.add_argument('--no_gui', dest='no_gui', action='store_true')
    parser.set_defaults(no_gui=False)
    parser.add_argument('--test_mode', dest='test_mode', action='store_true')
    parser.set_defaults(test_mode=False)


    parser.add_argument('--parametric', dest='cont_type', action='store_const', const="parametric")
    parser.add_argument('--weighted', dest='cont_type', action='store_const', const="weighted")

    return parser

if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    
    main(visualize=not args.no_gui, parallel=args.parallel, cont_type=args.cont_type, test_mode=args.test_mode)