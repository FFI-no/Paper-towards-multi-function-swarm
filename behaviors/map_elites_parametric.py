from map_elites_base import MAPElitesBase
from neat import nn
from math import atan, cos, sin, exp

import random
import cPickle
import numpy as np
import tinyarray as ta
import matplotlib as mpl
import matplotlib.patches as  mplpatch

import collections

id = 0

class MAPElitesParametric(MAPElitesBase):
    def __init__(self, agent, config):
        super(MAPElitesParametric, self).__init__(agent,config)
        
        self._weights = self.config["weights"]

        center_spreads = zip(self.config["center"], self.config["spread"])
        center_spreads = sorted(center_spreads)
        self._center = map(lambda v: v[0], center_spreads)
        self._spread = map(lambda v: v[1], center_spreads)
        self._scale = self.config["scale"]

        assert len(self._weights)==4, "Wrong number of weight parameters "
        assert len(self._center)==4, "Wrong number of center parameters "
        assert len(self._spread)==4, "Wrong number of spread parameters "
        assert len(self._scale)==4, "Wrong number of scale parameters "

        self.localization_history = collections.deque(maxlen=10) 

        global id

        self._id = id
        id += 1

        self._savedpatches = []    

        
    def _calc_force_contribution(self, directions, ranges):
        assert len(directions)==4, "Expected 4 directions got %s" % len(directions)
        assert len(ranges)==4, "Expected 4 ranges got %s" % len(ranges)

        total_force = ta.array([0.,0.])
        #print "ID: ", self._id

        self._forces = []
        for direction, range_, weight, center, spread, scale in zip(directions, ranges, self._weights, self._center, self._spread, self._scale):
            if direction is None:
                continue

            direction -= 3.14/2.
            direction = float(int(direction*100)%628)/100.

            unit_direction = ta.array([np.cos(direction), np.sin(direction)])

            if range_ is None:
                if weight < 0.01:
                    continue
                force = unit_direction*weight
            else:                
                exponent = -(range_-center)/spread
                exponent = min(8.,max(-8.,exponent))
                sigmoid = ((2./(1. + exp(exponent))) - 1.) * weight

                exponent = -(range_-center)**2/spread**2
                exponent = min(8.,max(-8.,exponent))
                well = -2*(range_-center) * scale * exp(exponent)
                
                force = unit_direction*(sigmoid+well)

            total_force = total_force + force
            self._forces.append(force)

        return total_force/len(directions)

    def get_update(self, current_time, case):
        if self.agent.platform.position is None:
            print "Warning position is none"
            return 

        directions, ranges = self._generate_inputs(case, self.agent.platform.position)
        velocity = self._calc_force_contribution(directions, ranges)

        self.agent.platform.set_velocity(velocity*self.agent.platform.max_velocity)

        dt = self.config["interval"]
        return [(current_time+dt, self.get_update)]
        
    def get_patches(self):
        return []