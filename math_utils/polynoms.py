# -*- coding:Utf-8 -*-


from . import expressions as mexpr
from . import math_sets
from typing import Any, Union, Sequence, Mapping, Set, AbstractSet


class PolynomTerm(mexpr.AbstractTerm):
    def __init__(self, term: mexpr.AbstractTerm) -> None:
        if not term.is_polynom_term():
            raise ValueError('this term is not valid for a polynom')
        self._term = term
        
    def __getattribute__(self, attr_name: str) -> Any:
        term = object.__getattribute__(self, '_term')
        if hasattr(term, attr_name):
            return getattr(term, attr_name)
        else:
            return object.__getattribute__(self, attr_name)
        
    def __add__(self, value: Any) -> Any:
        return self._term + value
    
    def __neg__(self) -> Any:
        return PolynomTerm(-self._term)
        
    def __sub__(self, value: Any) -> Any:
        return self._term - value
    
    def __mul__(self, value: Any) -> Any:
        return self._term * value
    
    def __rmul__(self, value: Any) -> Any:
        return value * self._term


