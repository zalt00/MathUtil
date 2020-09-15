
# -*- coding:Utf-8 -*-

from .plugin_base_class import Plugin
import matplotlib.pyplot as plt
import numpy as np
import math


class PlottingPlugin(Plugin):
    def __init__(self):
        super().__init__()
        
        self.add_action(self.define_plot_function)
        
    def plot(self, function, interval, precision=200, threshold_max=math.inf, threshold_min=-math.inf):
        array_x = np.linspace(interval.start, interval.stop, precision)
        array_y = np.zeros(precision, dtype=np.float64)
        
        for i, x in enumerate(array_x.flat):
            value = function(x)
            if value < threshold_min or value > threshold_max:
                value = math.nan
            array_y[i] = value
        
        plt.plot(array_x, array_y)
        plt.show()
        
    def define_plot_function(self, line, locals_, globals_):
        if 'plot' not in globals_:
            globals_['plot'] = self.plot
        return line
