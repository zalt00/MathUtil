# -*- coding:Utf-8 -*-

from .plugin_base_class import Plugin
from math_utils.math_sets import ListSet, Interval, NULL, REAL, RELATIVE, NATURAL
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
        
        self.add_action(self.base_sets_parser)
        
        self.list_sets_re = re.compile(r'\{([^,:}]*?)\}')
        self.add_action(self.list_sets_parser)
        
        self.interval_sets_re = re.compile(r'([][])([^,:[\]]*?);([^,:[\]]*?)([][])')
        self.add_action(self.interval_sets_parser)
        
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
    
    def base_sets_parser(self, line, locals_, globals_):
        for var_name, var in (('NULL', NULL), ('REAL', REAL), ('RELATIVE', RELATIVE), (NATURAL, 'NATURAL')):
            if var_name not in globals_:
                globals_[var_name] = var
                
        line = line.replace('ℝ', 'REAL').replace('∈', ' in ').replace('∅', 'NULL').replace('\\', '-').replace('U', ' | ')
        return line
    
    def list_sets_parser(self, line, locals_, globals_):
        if 'ListSet' not in globals_:
            globals_['ListSet'] = ListSet
        line = self.list_sets_re.sub(self._list_sets_parser_repl, line)
        
        return line
    
    @staticmethod
    def _list_sets_parser_repl(match):
        return f'ListSet(({match.group(0).replace(";", ",")}))'
    
    def interval_sets_parser(self, line, locals_, globals_):
        if 'Interval' not in globals_:
            globals_['Interval'] = Interval
        
        line = self.interval_sets_re.sub(self._interval_sets_parser_repl, line)
        return line

    @staticmethod
    def _interval_sets_parser_repl(match):
        if match.group(1) == '[':
            instart = True
        else:
            instart = False
            
        if match.group(4) == ']':
            instop = True
        else:
            instop = False
            
        start = match.group(2)
        stop = match.group(3)
        return f'Interval({start}, {stop}, {instart}, {instop})'
            
        
        

