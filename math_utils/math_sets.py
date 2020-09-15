# -*- coding:Utf-8 -*-


class Set:
    def __init__(self, contains_function):        
        self.contains = contains_function
        
    def __contains__(self, n):
        return self.contains(n)
    
    def __sub__(self, other_set):
        def contains(n):
            return (self.contains(n) and not other_set.contains(n))
        return Set(contains)
    
    def __or__(self, other_set):
        def contains(n):
            return (self.contains(n) or other_set.contains(n))
        return Set(contains)
    
    def __invert__(self):
        def contains(n):
            return not self.contains(n)
        return Set(contains)
    
    def __and__(self, other_set):
        def contains(n):
            return (self.contains(n) and other_set.contains(n))
        return Set(contains)

NULL = Set(lambda _: False)
REAL = Set(lambda n: isinstance(n, (int, float)))
RELATIVE = Set(lambda n: isinstance(n, int))
NATURAL = Set(lambda n: isinstance(n, int) and n > -1) 

class ListSet(Set):
    def __init__(self, container):
        self._container = container
        super().__init__(self.contains)
        
    def contains(self, n):
        return n in self._container
    
    def __repr__(self):
        return '{' + ";".join((repr(v) for v in self._container)) + '}'


class Interval(Set):
    def __init__(self, start, stop, include_start, include_stop):
        if start > stop:
            raise ValueError('start cannot be greater than stop')
            
        else:
            self.start_exclusiv = not include_start
            self.stop_exclusiv = not include_stop
            self.start = start
            self.stop = stop
            super().__init__(self.contains)
    
    def __repr__(self):
        a = ']' if self.start_exclusiv else '['
        b = '[' if self.stop_exclusiv else ']'
        return f'{a}{self.start};{self.stop}{b}'
    
    def contains(self, n):
        if self.start_exclusiv:
            con = self.start < n
        else:
            con = self.start <= n
            
        if self.stop_exclusiv:
            con &= n < self.stop
        else:
            con &= n <= self.stop
        
        return con
        




