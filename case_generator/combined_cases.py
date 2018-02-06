

import numpy as np
import random

from case import Case

class CombinedCases(object):
    def __init__(self, grid_size, num_cases, num_agents):
        self.grid_size = np.array(grid_size)
        self.num_cases = num_cases
        self.num_agents = num_agents
        
    def __iter__(self):
        np.random.seed(random.randint(0,1000000))
        
        self.current_index = 0
        
        return self
        
    def next(self):
        if self.current_index >= self.num_cases:
            raise StopIteration
            
        name = "%s %s" % (self.__class__.__name__, self.current_index)
        
        config = {}
        
        config['name'] = name
        
        config["config_agents"] = {"adv": self.num_agents}

        config["platform_templates"] = {}
        
        config["platform_templates"]["adv"] = {}
        config["platform_templates"]["adv"]["type"] = "Quadcopter"
        config["platform_templates"]["adv"]["config_platform"] = {"max_velocity": 10.0, "max_acceleration": 1.0, "interval": 1.0}
        config["platform_templates"]["adv"]["config_sensors"] = {}
        config["platform_templates"]["adv"]["config_sensors"]["Coverage"] = {}
        config["platform_templates"]["adv"]["config_sensors"]["Relay"] = {"range": 200}
        
        config["config_simulator"] = {"max_time": 1600.0, "view_delay": 6.0, "log_delay": 10.0, "grid_size": [1000.0, 1000.0]}
        
        self.current_index += 1
        
        return config
        
            
