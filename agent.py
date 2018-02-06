#!/usr/bin/python

import os
import os.path 
import traceback,sys

def list_modules(folder):
    types = []
    for f in os.listdir(folder):
        if os.path.isfile(os.path.join(folder,f)):
            try:
                name, extension = f.split(".")
                if extension == "py" and name != "__init__":
                    types.append(name)
            except:
                continue
    return types
    
def load_module(folder,name):
    try:
        module_list = list_modules(folder)
        module_list = dict([(filename.replace("_",""), filename) for filename in module_list]) 
        
        module = __import__("%s.%s" % (folder,module_list[name.lower()]), fromlist=[name])
    except ImportError:
        # Display error message
        traceback.print_exc(file=sys.stdout)
        raise ImportError("Failed to import module {0} from folder {1}".format(name,folder))
    return module

def select_class(name, name_list):
    for n, c in name_list:
        if n == name:
            return c

class Agent(object):
    def __init__(self, config):        
        assert config.get("config_platform") is not None, "Configuration for platform was not found"
        assert config.get("type") is not None, "Type of platform was not specified"
        self.platform = self._setup_platform(config["type"],config["config_platform"])
        
        
        assert config.get("config_sensors") is not None, "Configuration for sensors was not found"
        self.sensors = self._setup_sensors(config["config_sensors"])
        
        if config.get("behavior") is not None:
            self.behavior = self._load_behavior(config["behavior"], config["config_behavior"])
        else:
            self.behavior = None
            print "Warning no behaviour initialized for %s" % (type(self.platform))
        
    def _setup_sensors(self, config_sensors):
        sensors = {}
        for sensor_name, sensor_parameters in config_sensors.items():
            module = load_module("sensors", sensor_name)
            sensor = getattr(module, sensor_name)
            sensors[sensor_name] = sensor(self, sensor_parameters)
            
        return sensors
            
    def _setup_platform(self, platform_type, config_platform):
        module = load_module("platforms", platform_type)
        
        platform = getattr(module, platform_type)
        
        return platform(self, config_platform)
        
    def _load_behavior(self, behavior, config_behavior):
        module = load_module("behaviors", behavior)
        
        behavior_class = getattr(module, behavior)
        
        return behavior_class(self, config_behavior)
    
    def bootstrap_events(self, current_time, case, *args, **kwargs):
        result_events = []
            
        events = self.platform.step(current_time, case, *args, **kwargs)
        result_events.extend(events)
        
        if self.behavior is not None:
            events = self.behavior.get_update(current_time, case)
            
            result_events.extend(events)
            
        return result_events
           
    def __getstate__(self):
        state = self.__dict__.copy()
        return state
        
    def get_dict(self):
        return self.__getstate__()


