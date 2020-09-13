# -*- coding:Utf-8 -*-

from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence

class Plugin:
    def __init__(self):
        self._actions = []
        self._shortcuts = []
    
    def add_shortcut(self, str_sequence, command_name, command_args):
        if isinstance(command_args, str):
            command_args = [command_args]
        self._shortcuts.append((str_sequence, command_name, command_args))
    
    def add_action(self, callback):
        self._actions.append(callback)
    
    def add_to(self, parent):
        for function in self._actions:
            parent.add_sequence(function)
        
        for str_sequence, command_name, command_args in self._shortcuts:
            command = self._get_command(parent.commands[command_name], command_args)
            parent.add_shortcut(str_sequence, command)
        
    def _get_command(self, command, command_args):
        def callback():
            return command(*command_args)
        return callback
    


