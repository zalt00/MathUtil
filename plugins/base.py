# -*- coding:Utf-8 -*-

from .plugin_base_class import Plugin


class BasePlugin(Plugin):
    def __init__(self):
        super().__init__()
        
        self.add_shortcut('Return', 'execute_current_line', [])
        