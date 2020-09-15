# -*- coding:Utf-8 -*-


def get_plugin(plugin_name):
    return globals()[plugin_name]

# plug-in imports
from .base_math import BaseMathPlugin
from .base import BasePlugin
from .math_plot import PlottingPlugin