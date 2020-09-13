# -*- coding:Utf-8 -*-

from .plugin_base_class import Plugin
import re
import math

class BaseMathPlugin(Plugin):
    def __init__(self):
        super().__init__()
        
        self.add_shortcut('Alt+i', 'insert_key', '∞')
        self.add_shortcut('Alt+a', 'insert_key', '∀')
        self.add_shortcut('Alt+r', 'insert_key', 'ℝ')
        self.add_shortcut('Alt+c', 'insert_key', '∈')
        self.add_shortcut('Alt+o', 'insert_key', '∅')
        self.add_shortcut('Ctrl+-', 'insert_key', '⁻')
        self.add_shortcut('Alt+s', 'insert_key', '√(')
        self.add_shortcut('Ctrl+9', 'insert_key', '⁹')
        self.add_shortcut('Ctrl+8', 'insert_key', '⁸')
        self.add_shortcut('Ctrl+7', 'insert_key', '⁷')
        self.add_shortcut('Ctrl+6', 'insert_key', '⁶')
        self.add_shortcut('Ctrl+5', 'insert_key', '⁵')
        self.add_shortcut('Ctrl+4', 'insert_key', '⁴')
        self.add_shortcut('Ctrl+3', 'insert_key', '³')
        self.add_shortcut('Ctrl+2', 'insert_key', '²')
        self.add_shortcut('Ctrl+1', 'insert_key', '¹')
        self.add_shortcut('Ctrl+0', 'insert_key', '⁰')
        
        self.power_re = re.compile(r'(⁻?[⁰¹²³⁴⁵⁶⁷⁸⁹]+)')
        self.add_action(self.power_parser)
        
        self.sqrt_re = re.compile(r'√([(].+[)])')
        self.add_action(self.sqrt_parser)
        
        self.function_re = re.compile(r'([fghpijklm])[(]x[)][ ]?=(.*)')
        self.add_action(self.function_parser)
        
        self.multiplication_re = re.compile(r'(\d)([a-z])')
        self.add_action(self.multiplication_parser)
        
        self.add_action(self.inf_parser)
        
    def power_parser(self, line, locals_, globals_):
        line = self.power_re.sub(r'**\1', line)
        line = line.replace('⁻', '-').replace('⁰', '0').replace('¹', '1').replace('²', '2').replace('³', '3').replace('⁴', '4').replace('⁵', '5')
        line = line.replace('⁶', '6').replace('⁷', '7').replace('⁸', '8').replace('⁹', '9')
        return line
    
    def sqrt_parser(self, line, locals_, globals_):
        if 'sqrt' not in globals_:
            globals_['sqrt'] = math.sqrt
        
        line = self.sqrt_re.sub(r'sqrt\1', line)
        return line
    
    def function_parser(self, line, locals_, globals_):
        line = self.function_re.sub(r'\1 = lambda x: \2', line)
        return line
        
    def multiplication_parser(self, line, locals_, globals_):
        line = self.multiplication_re.sub(r'\1 * \2', line)
        return line
    
    def inf_parser(self, line, locals_, globals_):
        if 'inf' not in globals_:
            globals_['inf'] = math.inf
            
        line = line.replace('∞', 'inf')
        return line


