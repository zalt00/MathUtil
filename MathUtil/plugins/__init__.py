# -*- coding:Utf-8 -*-

from .base_math import BaseMathPlugin
from .base import BasePlugin


def get_plugin(plugin_name):
    return globals()[plugin_name]
