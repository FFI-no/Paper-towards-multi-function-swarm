from behavior import Behavior
from neat import nn
from math import atan, cos, sin, exp

import random
import cPickle
import numpy as np
import tinyarray as ta
import matplotlib as mpl
import matplotlib.patches as  mplpatch

import collections


class MAPElitesBase(Behavior):
    def __init__(self, agent, config):
        self.agent = agent
        self.config = config        
        
    def _generate_inputs(self, case, self_position):  

        i,j = map(int,self_position/100.0)
        
        ranges = []
        directions = []
                
        neighbours = []
        
        for agent in case.agents:
            if self.agent == agent:
                continue 
                
            position = agent.platform.position
            delta = position-self_position
            distance = np.linalg.norm(delta)
            direction = 3.14-np.arctan2(*delta)
            neighbours.append((direction, distance))
            
            
        neighbours = sorted(neighbours, key=lambda v: v[1])
        
        for direction, distance in neighbours[:3]:
            directions.append(direction)
            ranges.append(distance)

        if self.agent.sensors.get('Coverage') is not None:
            squares = []
            for o_i in range(-1, 2, 1):
                for o_j in range(-1, 2, 1):
                    if 0 <= o_i + i <= 9 and 0 <= o_j + j <= 9:
                        squares.append(((o_i+i, o_j+j), case.blackboard["Coverage"][i+o_i,j+o_j]))
                        
            _, min_value = min(squares, key=lambda v: v[1])
            equal_to_min_squares = filter(lambda v: v[1] <= min_value+0.01, squares)
            min_direction, min_value = random.choice(equal_to_min_squares)
            
            angle = 3.14-np.arctan2(*(min_direction-ta.array([i,j])))
            
            directions.append(angle)
            ranges.append(None)
        else:
            directions.append(None)
            ranges.append(None)
            
            
        # if self.agent.sensors.get('Localization') is not None:
        #     self.localization_history.append(self.agent.sensors['Localization'].localization)
            
        #     avg_position = reduce(lambda x,y: x+y, self.localization_history) / len(self.localization_history)
            
        #     delta = avg_position - self_position
        #     distance = np.linalg.norm(delta)
        #     direction = 3.14-np.arctan2(*delta)
            
        #     directions.append(direction)
        #     ranges.append(distance)
        # else:
        #     directions.append(None)
        #     ranges.append(None)
            
                    
        return directions, ranges
        

        
