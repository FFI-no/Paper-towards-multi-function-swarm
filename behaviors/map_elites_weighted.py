from map_elites_base import MAPElitesBase
from neat import nn
from math import atan, cos, sin

import random
import cPickle
import numpy as np
import tinyarray as ta
import matplotlib as mpl
import matplotlib.patches as  mplpatch

import collections

mapelites_force_id = 0


class MAPElitesWeighted(MAPElitesBase):
    def __init__(self, agent, config):
        super(MAPElitesWeighted, self).__init__(agent,config)
        
        self._weights = self.config["weights"]
        assert len(self._weights)==4, "Wrong number of weights for MAPElitesWeighted (%s != %s)" % (len(self._weights), 4)
        
        self.localization_history = collections.deque(maxlen=10) 

        global mapelites_force_id

        self._id = mapelites_force_id
        mapelites_force_id += 1

        self._savedpatches = []
        
    def _calc_force_contribution(self, directions, ranges, weights):
        assert len(directions)==4, "Expected 4 directions got %s" % len(directions)
        assert len(ranges)==4, "Expected 4 ranges got %s" % len(ranges)

        total_force = ta.array([0.,0.])

        self._forces = []
        for d, r, w in zip(directions, ranges, weights):
            if d is None:
                continue
                
            d -= 3.14/2
            d = float(int(d*100)%628)/100

            force = ta.array([np.cos(d), np.sin(d)])*w
            self._forces.append(force)
            total_force = total_force + force

        return total_force/len(directions)

    def get_update(self, current_time, case):      
        directions, ranges = self._generate_inputs(case, self.agent.platform.position)
        velocity = self._calc_force_contribution(directions, ranges, self._weights)
        self.agent.platform.set_velocity(velocity*self.agent.platform.max_velocity)
        
        dt = self.config["interval"]
        return [(current_time+dt, self.get_update)]
        
    def get_patches(self):
        return []