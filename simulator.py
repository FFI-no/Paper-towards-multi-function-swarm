import tasks

from time import sleep
from case import Case
from logger import Logger
from visualize_case import VisualizeCase

def count_status(results_inprogress):
    statuses = map(lambda x: x.status, results_inprogress)
    started = len(filter(lambda x: x == "STARTED", statuses))
    pending = len(filter(lambda x: x == "PENDING", statuses))
    finished = len(filter(lambda x: x == "SUCCESS", statuses))
    failed =  len(filter(lambda x: x == "FAILURE", statuses))

    return started, pending, finished, failed
    
def filter_status(results_inprogress, status):
    f = filter(lambda x: x.state == status, results_inprogress)
    nf = filter(lambda x: x.state != status, results_inprogress)

    return f, nf
    
def wait_for_parallel_completion(results_inprogress):
    num_tasks = len(results_inprogress)
    
    old_finished_count = -1
    
    while len(results_inprogress) > old_finished_count:
        try:
            started, pending, finished, failed = count_status(results_inprogress)
            
            if old_finished_count != finished:
                print "Pending: %s" % pending
                print "Finished: %s" % finished
                print "Failed: %s" % failed
                print
                
                old_finished_count = finished
            
            
            assert failed==0, "Some tasks failed, aborting"
           
            sleep(1)
            
        except (AssertionError, KeyboardInterrupt, SystemExit), e:
            for task in results_inprogress:
                task.revoke(terminate=True)
            print "Exiting."
            raise KeyboardInterrupt

    print "All tasks completed"

def run_simulations_parallel(pairs):
    k_async_results = []

    for k, case_configs in pairs:
        r  = [tasks.run_case.delay(case_config) for case_config in case_configs]
        
        k_async_results.append((k,r))

    wait_for_parallel_completion(reduce(lambda a, b: a+b, map(lambda p: p[1], k_async_results)))

    k_logs = []

    for k, async_results in k_async_results:
        logs =  [result.get() for result in async_results]
        [result.forget() for result in async_results]

        k_logs.append((k, logs))

    return k_logs


def run_simulation(config, visualize=False):
    case = Case(config)

    if visualize:
        visualization = VisualizeCase(case)
    else:
        visualization = None
    
    logger = Logger(case, None, prefix_folder="logs")
    with logger as open_logger:

        with case as expanded_case:
            expanded_case.run(logger=open_logger, visualization=visualization)
        
    print "Completed simulation: %s" % str(case)

    if visualization is not None:
        visualization.close()
    
    return logger

def run_simulations_serial(pairs, visualize=False):
    k_logs = []

    for k, case_configs in pairs:
        logs  = [run_simulation(case_config, visualize) for case_config in case_configs]  
        k_logs.append((k, logs))

    return k_logs

