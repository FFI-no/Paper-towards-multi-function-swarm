

import numpy as np
#import tinyarray as ta
ta = np
import matplotlib.patches as  mplpatch


from sensor import Sensor

def vec_norm(vec):
    return np.sqrt(ta.dot(vec, vec)) 



class Relay(Sensor):
    def __init__(self, agent, config):
        super(Relay, self).__init__(agent, config)
        
        self.connections = []
        
        self._range = config["range"]
        
        
        
    def update(self, platform, case):
        super(Relay, self).update(platform, case)
        
        self.connections = []
        
        
        for agent in case.agents:
            if agent.platform is platform or not agent.platform.has_sensor(type(self)):
                continue
            
            d = vec_norm(agent.platform.position - platform.position)
            if d < self._range:
                self.connections.append(agent)
                
        
        #Grid map opt, for all to all ranging
        #for _,agent in case.collisions.collides_with(self.agent, self.config["range"]):
            #if agent is self.agent or not agent.platform.has_sensor(type(self)):
                #continue
                
            #self.connections.append(agent)
                
                
            
    
    def get_patches(self):
        if self.position is not None:
            import matplotlib.pyplot as plt
            import matplotlib.colors as colors
            import matplotlib.cm as cmx
            jet = cm = plt.get_cmap('Greens') 
            cNorm  = colors.Normalize(vmin=0, vmax=100)
            scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
            
            patches = []
            
            # patch = mplpatch.Circle(
            #         self.agent.platform.position,   # (x,y)
            #         self.config["range"],  
            #         zorder=-2,
            #         edgecolor="r",
            #         fill=False)
                
            # patches.append(patch)
            
            arrow  = mplpatch.ArrowStyle.Simple()
            for connection in self.connections:
                dx, dy = connection.platform.position - self.position
                
                #patch = mplpatch.Arrow( self.position[0], self.position[1], dx, dy, 10, zorder=-1, fc="g")
                #patch = mplpatch.FancyArrowPatch( connection.platform.position, self.position,zorder=-1, c="g")
                c = (0,0,0)
                patch = mplpatch.FancyArrow( self.position[0], self.position[1], dx, dy, head_width=0, width=4, zorder=-1, ec=c, fc=c )
                patches.append(patch)
                       
                # distance = np.sqrt(dx**2 + dy**2) 
                
                # patch = mplpatch.Circle(
                #         self.position,   # (x,y)
                #         distance,  
                #         zorder=-2,
                #         facecolor=scalarMap.to_rgba(distance * 100. / self._range),
                #         edgecolor="r",
                #         alpha=0.5)
                # patches.append(patch)
            
            # if len(self.connections) > 0:                
            #     patch = mplpatch.Circle(
            #             self.position,   # (x,y)
            #             self._range,  
            #             zorder=-2,
            #             facecolor="g",
            #             edgecolor=(0.,0.,0.),
            #             alpha=0.5)
            #     patches.append(patch)
            
            return patches
            
        else:
            return []
