
import numpy as np
#import tinyarray as ta
ta = np

import random

import matplotlib.patches as  mplpatch

class Platform(object):
    def __init__(self, agent, config):
        self.agent = agent
        
        self.position = ta.array([random.randint(0,1000), random.randint(0,1000)], float)
        
    def has_sensor(self, sensor_type, string=False):
        if string:
            for sensor in self.agent.sensors.values():
                if sensor_type in str(type(sensor)):
                    return True
                    
            return False

        else:
            for sensor in self.agent.sensors.values():
                if type(sensor) == sensor_type:
                    return True
                    
            return False
        
    def step(self, current_time, case):
        for sensor in self.agent.sensors.values():
            sensor.update(self, case)

        return []
        
        
    def set_position(self, position):
        raise NotImplemented
        
        
    def get_patches(self):
        return  []
        
        patch = mplpatch.Circle(
                self.position,   # (x,y)
                10,  
                zorder=0,
                color="r")
        return [patch]

        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state['priority_queue']
        del state['_previous_positions']
        return state
        
    def __getstate__(self):
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state['agent']
        return state
        
    def get_dict(self):
        return self.__getstate__()
