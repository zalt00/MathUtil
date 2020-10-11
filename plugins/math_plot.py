
# -*- coding:Utf-8 -*-

from .plugin_base_class import Plugin
import matplotlib.pyplot as plt
import numpy as np
import math


class PlottingPlugin(Plugin):
    def __init__(self):
        super().__init__()
        
        self.add_action(self.define_plot_function)
        
    def plot(self, function, interval, precision=1000, threshold_max=math.inf, threshold_min=-math.inf):
        array_x = np.linspace(interval.start, interval.stop, precision)
        array_y = np.zeros(precision, dtype=np.float64)
        no_definition_points = []
        
        for i, x in enumerate(array_x.flat):
            if math.isnan(function(round(x, 1))):
                value = math.nan
            else:
                value = function(x)
            if value < threshold_min or value > threshold_max:
                value = math.nan
            if math.isnan(value):
                no_definition_points.append(i)
            array_y[i] = value
        
        print(no_definition_points)
        
        previous_point = 0
        for point in no_definition_points:
            plt.plot(array_x[previous_point:point], array_y[previous_point:point])
            previous_point = point
        plt.plot(array_x[previous_point:], array_y[previous_point:])
        
        plt.show()
        
    def define_plot_function(self, line, locals_, globals_):
        if 'plot' not in globals_:
            globals_['plot'] = self.plot
        return line
