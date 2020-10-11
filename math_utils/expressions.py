# -*- coding:Utf-8 -*-

from collections import UserDict
from typing import Any, Union, Sequence, Mapping, Set, AbstractSet
from .math_sets import NATURAL


class Variables(UserDict):
    def __missing__(self, _: Any) -> int:
        return 0
    
    def __setitem__(self, key: Any, value: int) -> None:
        if value == 0:
            if key in self:
                self.pop(key)
        else:
            super().__setitem__(key, value)
    
    def __eq__(self, other_dict: Any) -> bool:
        if not isinstance(other_dict, Variables):
            try:
                other_dict = Variables(other_dict)
            except TypeError:
                return NotImplemented
            
        for key in self.keys() | other_dict.keys():
            if self[key] != other_dict[key]:
                return False
            
        return True
    
    def length_without_null_values(self) -> int:
        return len(list(v for v in self.values() if v != 0))

Map = Union[Mapping, Variables]


class AbstractTerm:
    
    def __init__(self) -> None:
        self._variables: Map = {}
        self.multiplier: int = 1
    
    @property
    def degree(self): raise NotImplementedError
    def __add__(self, value): raise NotImplementedError
    def __neg__(self): raise NotImplementedError
    def __sub__(self, value): raise NotImplementedError
    def __mul__(self, value): raise NotImplementedError
    def __rmul__(self, value): raise NotImplementedError
    def is_null(self): raise NotImplementedError
    def develop(self): raise NotImplementedError
    def is_polynom_term(self) -> bool: return False
    @property
    def variable_names(self): raise NotImplementedError
    
    @property
    def variables(self) -> Map:
        return self._variables
    
    @variables.setter
    def variables(self, value: Map):
        if not isinstance(value, Variables):
            self._variables = Variables(value)
        else:
            self._variables = value
    

class AbstractExpression:
    remove_null_values_when_repr = True
    term: AbstractTerm
    @property
    def degree(self): raise NotImplementedError
    def __imul__(self, value): raise NotImplementedError
    def __mul__(self, value): raise NotImplementedError
    def copy(self): raise NotImplementedError
    def __iadd__(self, value) -> Any: raise NotImplementedError
    def __add__(self, value) -> Any: raise NotImplementedError
    def __isub__(self, value): raise NotImplementedError
    def __sub__(self, value): raise NotImplementedError
    def __neg__(self): raise NotImplementedError
    def get_all_terms(self): raise NotImplementedError
    def remove_null_values(self): raise NotImplementedError
    def __eq__(self, expr): raise NotImplementedError
    def is_null(self): raise NotImplementedError
    def develop(self): raise NotImplementedError
    @property
    def variable_names(self): raise NotImplementedError
    def is_polynom(self) -> bool: return False


TermOrExpression = Union[AbstractTerm, AbstractExpression]

class Term(AbstractTerm):
    def __init__(self, multiplier: int, **variables) -> None:
        super().__init__()
        self.multiplier = multiplier
        self.variables = variables
        
    @property
    def degree(self) -> int:
        total = 0
        for deg in self.variables.values():
            total += deg
        return total
    
    def __repr__(self) -> str:
        txt = str(self.multiplier) * (self.multiplier != 1 or self.degree == 0)
        for var_name, degree in self.variables.items():
            if degree not in {0, 1}:
                degree_repr = str(degree)
                degree_repr = degree_repr.replace('-', '⁻').replace('0', '⁰').replace('1', '¹').replace('2', '²').replace('3', '³').replace('4', '⁴').replace('5', '⁵')
                degree_repr = degree_repr.replace('6', '⁶').replace('7', '⁷').replace('8', '⁸').replace('9', '⁹')
            elif degree == 0:
                degree_repr = ''
                var_name = ''
            else:
                degree_repr = ''
            txt += f'{var_name}{degree_repr}'
        return txt

    def __add__(self, value: TermOrExpression) -> TermOrExpression:
        if isinstance(value, AbstractExpression):
            return value + self
        elif isinstance(value, AbstractTerm):
            if value.variables == self.variables:
                return Term(self.multiplier + value.multiplier, **self.variables)
            else:
                return Expression(self) + value
        else:
            return NotImplemented
    
    def __neg__(self) -> AbstractTerm:
        return Term(-self.multiplier, **self.variables)
    
    def __sub__(self, value: TermOrExpression) -> TermOrExpression:
        return self + (-value)
    
    def __mul__(self, value: Union[TermOrExpression, int]) -> AbstractTerm:
        if isinstance(value, int):
            return Term(self.multiplier * value, **self.variables)
        elif isinstance(value, AbstractExpression):
            return TermExpressionMultiplicationTerm(Expression(self, None), value)
        elif isinstance(value, AbstractTerm):
            return TermTermMultiplicationTerm(Expression(self, None), Expression(value, None))
        else:
            return NotImplemented
    
    def __rmul__(self, value: Union[TermOrExpression, int]) -> AbstractTerm:
        return self * value
    
    def is_null(self) -> bool:
        return self.multiplier == 0
    
    def develop(self) -> AbstractTerm:
        return self
    
    @property
    def variable_names(self) -> Union[AbstractSet[str], Sequence[str]]:
        return self.variables.keys()
    
    def is_polynom_term(self) -> bool:
        return self.degree in NATURAL and self.variables.length_without_null_values() <= 1


class Expression(AbstractExpression):
    def __init__(self, term: AbstractTerm, rest_of_expression: Union[None, AbstractExpression] = None):
        self.term = term
        self.rest_of_expression = rest_of_expression
    
    def __imul__(self, value: Union[TermOrExpression, int]) -> AbstractExpression:
        if isinstance(value, int):
            self.term *= value
            if self.rest_of_expression is not None:
                self.rest_of_expression *= value
        elif isinstance(value, AbstractExpression):
            term = ExpressionMultiplicationTerm(self, value)
            expression = Expression(term, None)
            return expression
        elif isinstance(value, AbstractTerm):
            return Expression(value * self)
        else:
            return NotImplemented
        return self
        
    def __mul__(self, value: Union[TermOrExpression, int]) -> AbstractExpression:
        new_expression = self.copy()
        new_expression *= value
        return new_expression
        
    def copy(self) -> AbstractExpression:
        if self.rest_of_expression is None:
            return Expression(self.term, None)
        else:
            return Expression(self.term, self.rest_of_expression.copy())
        
    def __iadd__(self, value: TermOrExpression) -> Any:
        if isinstance(value, AbstractTerm):
            if self.term.variables == value.variables:
                self.term += value
            else:
                if self.rest_of_expression is None:
                    self.rest_of_expression = Expression(value)
                else:
                    self.rest_of_expression += value
                    
        elif isinstance(value, AbstractExpression):
            for term in value.get_all_terms():
                self += term
        else:
            return NotImplemented
        return self
        
    def __add__(self, value: TermOrExpression) -> AbstractExpression:
        new_expression = self.copy()
        new_expression += value
        return new_expression
    
    def __isub__(self, value: TermOrExpression) -> AbstractExpression:
        self += (-value)
        return self
            
    def __sub__(self, value: TermOrExpression) -> AbstractExpression:
        new_expression = self.copy()
        new_expression -= value
        return new_expression
    
    def __neg__(self) -> AbstractExpression:
        return self * -1
    
    def get_all_terms(self) -> Set[AbstractTerm]:
        terms = {self.term}
        if self.rest_of_expression is None:
            return terms
        else:
            return terms | self.rest_of_expression.get_all_terms()
        
    def __repr__(self) -> str:
        if self.remove_null_values_when_repr:
            expr = self.remove_null_values()
            if expr is None:
                return '0'
        else:
            expr = self
        terms = sorted(expr.get_all_terms(), key=lambda m: m.degree)

        txt = str(terms.pop())
        for term in reversed(terms):
            if term.multiplier < 0:
                txt += f' - {-term}'
            else:
                txt += f' + {term}'
        
        return txt
    
    def is_null(self) -> bool:
        return self.remove_null_values() is None
    
    def remove_null_values(self) -> Union[None, AbstractExpression]:
        if self.term.is_null():
            if self.rest_of_expression is None:
                return None
            else:
                return self.rest_of_expression.remove_null_values()
        else:
            new_expression = Expression(self.term, self.rest_of_expression)
            if new_expression.rest_of_expression is not None:
                new_expression.rest_of_expression = new_expression.rest_of_expression.remove_null_values()
            return new_expression
    
    @property
    def degree(self) -> int:
        if self.rest_of_expression is not None:
            return max(self.rest_of_expression.degree, self.term.degree)
        else:
            return self.term.degree
    
    def __eq__(self, expr: object) -> bool:
        if isinstance(expr, AbstractExpression):
            return self.get_all_terms() == expr.get_all_terms()
        return False
    
    def develop(self) -> AbstractExpression:
        if self.rest_of_expression is None:
            return self.term.develop()
        else:
            return self.term.develop() + self.rest_of_expression.develop()
    
    @property
    def variable_names(self) -> Sequence[str]:
        if self.rest_of_expression is None:
            return self.term.variable_names
        else:
            return self.term.variable_names | self.rest_of_expression.variable_names
        
    def is_polynom(self) -> bool:
        if self.rest_of_expression is None:
            return self.term.is_polynom_term()
        else:
            return self.term.is_polynom_term() and self.rest_of_expression.is_polynom()
    
    
class ExpressionMultiplicationTerm(AbstractTerm):
    def __init__(self, expr_1: AbstractExpression, expr_2: AbstractExpression, multiplier: int = 1):
        super().__init__()
        self.expr_1 = expr_1
        self.expr_2 = expr_2
        self.multiplier = multiplier
        self.variables: Map = {'expr_1': self.expr_1, 'expr_2': self.expr_2}
        
    @property
    def degree(self) -> int:
        return self.expr_1.degree + self.expr_2.degree
    
    def __add__(self, value: TermOrExpression) -> TermOrExpression:
        if isinstance(value, AbstractExpression):
            return value + self
    
        elif isinstance(value, ExpressionMultiplicationTerm):
            if ((value.expr_1 == self.expr_1 and value.expr_2 == self.expr_2) or
                (value.expr_2 == self.expr_1 and value.expr_1 == self.expr_2)):
                return ExpressionMultiplicationTerm(self.expr_1.copy(), self.expr_2.copy(), self.multiplier + value.multiplier)
            else:
                return Expression(self) + value
        elif isinstance(value, AbstractTerm):
            return Expression(self) + value
            
        else:
            return NotImplemented
        
    def __neg__(self) -> AbstractTerm:
        return self * -1
    
    def __sub__(self, value: TermOrExpression) -> TermOrExpression:
        return self + (-value)
        
    def __mul__(self, value: Union[TermOrExpression, int]) -> AbstractTerm:
        if isinstance(value, int):
            return ExpressionMultiplicationTerm(self.expr_1.copy(), self.expr_2.copy(), self.multiplier * value)
        else:
            return NotImplemented            
    
    def __rmul__(self, value: Union[TermOrExpression, int]) -> AbstractTerm:
        return self * value
    
    def is_null(self) -> bool:
        return self.multiplier == 0 or self.expr_1.is_null() or self.expr_2.is_null()
    
    def __repr__(self) -> str:
        if self.multiplier != 1:
            return f'{self.multiplier}({self.expr_1})({self.expr_2})'
        else:
            return f'({self.expr_1})({self.expr_2})'
    
    def develop(self) -> Union[None, TermOrExpression]:
        terms = self.expr_1.get_all_terms()
        expression = None
        for term in terms:
            if expression is None:
                expression = term * self.expr_2
            else:
                expression += term * self.expr_2
        if expression is None:
            raise ValueError("terms' length must be higher than 0")
        return expression.develop()
    
    @property
    def variable_names(self) -> Sequence[str]:
        return self.expr_1.variable_names | self.expr_2.variable_names
    
    def is_polynom_term(self) -> bool:
        return self.expr_1.is_polynom() and self.expr_2.is_polynom()


class TermExpressionMultiplicationTerm(ExpressionMultiplicationTerm):
    def develop(self) -> Union[None, TermOrExpression]:
        factor = self.expr_1.term
        terms = self.expr_2.get_all_terms()
        expression = None
        for term in terms:
                
            if expression is None:
                expression = factor * term
            else:
                expression += factor * term
        if expression is None:
            raise ValueError("terms' length must be higher than 0")
        return expression.develop()


class TermTermMultiplicationTerm(TermExpressionMultiplicationTerm):
    def develop(self) -> Union[None, TermOrExpression]:
        factor = self.expr_1.term
        term = self.expr_2.term
        
        multiplier = term.multiplier * factor.multiplier
        
        if isinstance(factor.variables, Variables):
            variables = factor.variables.copy()
        else:
            variables = Variables(factor.variables)
            
        for var_name, value in term.variables.items():
            variables[var_name] += value
        
        new_term = Term(multiplier, **variables)
        return new_term
    

a = Term(1, x=1)
b = Term(1, x=0)
c = Term(2, x=4)
d = Term(2, x=5)
e = Term(2, x=6)
f = Term(2, x=7)
g = Term(2, x=8)
h = Term(2, x=9)

