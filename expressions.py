# -*- coding:Utf-8 -*-


from collections import UserDict
from typing import Any, Union, Sequence, Mapping, Set, AbstractSet
from types import MappingProxyType
import abc


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
    
    def __iadd__(self, variables2):
        if not isinstance(variables2, Variables):
            return NotImplemented
        for k, v in variables2.items():
            self[k] += v
        return self
    
    def length_without_null_values(self) -> int:
        return len(list(v for v in self.values() if v != 0))


class AbstractExpression(metaclass=abc.ABCMeta):
    def __init__(self, term, rest_of_expression):
        self.term = term
        self.rest_of_expression = rest_of_expression

    def copy(self):
        return type(self)(self.term.copy(), self.rest_of_expression.copy())
    
    @abc.abstractmethod
    def __iadd__(self, expr):
        if not isinstance(expr, AbstractExpression):
            return NotImplemented
        return self

    @abc.abstractmethod
    def __imul__(self, expr_or_n):
        if not isinstance(expr_or_n, (AbstractExpression, int)):
            return NotImplemented
        return self

    @abc.abstractmethod
    def __neg__(self):
        return self
    
    def __isub__(self, expr):
        self += -expr
        return self

    def __sub__(self, expr):
        copy = self.copy()
        copy -= expr
        return copy
    
    def __add__(self, expr):
        copy = self.copy()
        copy += expr
        return copy

    def __mul__(self, expr_or_n):
        copy = self.copy()
        copy *= expr_or_n
        return copy
        

    @abc.abstractmethod
    def __eq__(self, expr):
        if not isinstance(expr, AbstractExpression):
            return NotImplemented
        return self is expr

    def freeze(self):
        return FrozenExpression(self)
    
    def can_be_added_to(self, expr):
        if not isinstance(expr, AbstractExpression):
            raise TypeError('expr must be an AbstractExpression')
        return False


class FrozenExpression:
    def __init__(self, expr):
        if not isinstance(expr, AbstractExpression):
            raise TypeError('expr must be an AbstractExpression')
        self._expr = expr

    def __hash__(self):
        return hash((self.term.freeze(), self.rest_of_expression.freeze()))
    
    def __getattribute__(self, attr_name):
        try:
            return getattr(object.__getattribute__(self, '_expr'), attr_name)
        except AttributeError:
            pass
        return object.__getattribute__(self, attr_name)


class FrozenLiteralValue(FrozenExpression):
    def __init__(self, expr):
        super().__init__(expr)
        self._term.variables = MappingProxyType(self._term.variables)

    def __hash__(self):
        return hash((self.value, self._term.variables))
    
class AbstractSingleValueExpression(AbstractExpression):
    def __init__(self, value):
        self.value = value
        self.term = EmptyExpression()
        self.rest_of_expression = self.term.copy()
    

class EmptyExpression(AbstractExpression):
    def __init__(self):
        self.term = None
        self.rest_of_expression = None

    def copy(self):
        return EmptyExpression()

    def __iadd__(self, expr):
        return expr

    def __imul__(self, expr):
        return self

    def __neg__(self):
        return self

    def __eq__(self, expr):
        super().__eq__(expr)
        if isinstance(expr, EmptyExpression):
            return True
        return False

    def freeze(self):
        return self

    def __hash__(self):
        return 0


class Sum(AbstractExpression):
    def __init__(self, term, rest_of_expression):
        super().__init__(term, rest_of_expression)
        if isinstance(self.term, Sum):
            raise TypeError('term cannot be a Sum')
        
    def __repr__(self):
        return f'{self.term} + {self.rest_of_expression}'

    def __neg__(self):
        super().__neg__()
        return Sum(-self.term, -self.rest_of_expression)

    def __imul__(self, expr_or_n):
        super().__imul__(expr_or_n)
        return Product(self, expr_or_n)

    def __iadd__(self, expr):
        super().__iadd__(expr)
        if not isinstance(expr, EmptyExpression):
            if not isinstance(expr, Sum):
                if expr.can_be_added_to(self.term):
                    self.term += expr
                    if isinstance(self.term, Sum):
                        raise TypeError('term cannot be a Sum')
                else:
                    self.rest_of_expression += expr
                return self
            else:
                for term in expr.get_terms():
                    self += term
        return self

    def get_terms(self):
        s = {self.term.freeze()}
        if isinstance(self.rest_of_expression, Sum):
            s |= self.rest_of_expression.get_terms()
        return s

    def __eq__(self, expr):
        super().__eq__(expr)
        if isinstance(expr, Sum):
            return self.get_terms() == expr.get_terms()
        return False


class Product(AbstractExpression):
    def __init__(self, term, rest_of_expression):
        super().__init__(term, rest_of_expression)
        if isinstance(self.term, Product):
            raise TypeError('term cannot be a Sum')

    def __repr__(self):
        return f'({self.term})({self.rest_of_expression})'

    def __iadd__(self, expr):
        super().__iadd__(expr)
        if not isinstance(expr, EmptyExpression):
            if expr.can_be_added_to(self):
                return self * 2
            else:
                return Sum(self, expr)
        return self

    def __imul__(self, expr_or_n):
        super().__imul__(expr_or_n)
        if not isinstance(expr_or_n, EmptyExpression):
            if isinstance(expr_or_n, int):
                self.term *= expr_or_n
            elif not isinstance(expr_or_n, Product):
                self.rest_of_expression = Product(expr_or_n, self.rest_of_expression)
            else:
                for factor in expr_or_n.get_factors():
                    self *= factor
        return self

    def __neg__(self):
        return self * -1
    
    def get_factors(self):
        s = {self.term.freeze()}
        if isinstance(self.rest_of_expression, Product):
            s |= self.rest_of_expression.get_factors()
        return s

    def __eq__(self, expr):
        super().__eq__(expr)
        if isinstance(expr, Product):
            return self.get_factors() == expr.get_factors()
        return False

    def can_be_added_to(self, expr):
        return self == expr


class NumericValue(AbstractExpression):
    def __init__(self, value):
        super().__init__(EmptyExpression(), EmptyExpression())
        self.value = value

    def __iadd__(self, expr):
        super().__iadd__(expr)
        if not isinstance(expr_or_n, EmptyExpression):
            if isinstance(expr, NumericValue):
                self.value += expr.value
            else:
                return Sum(self, expr)
        return self

    def __imul__(self, expr):
        super().__imul__(expr)
        if not isinstance(expr_or_n, EmptyExpression):
            if isinstance(expr, NumericValue):
                self.value *= expr.value
            else:
                return Product(self, expr)
        return self

    def __neg__(self):
        return NumericValue(-self.value)

    def __repr__(self):
        return str(self.value)

    def copy(self):
        return NumericValue(self.value)

    


class LiteralValue(AbstractExpression):
    def __init__(self, value, **variables):
        super().__init__(EmptyExpression(), EmptyExpression())
        self.value = value
        self.variables = Variables(variables)

    def __iadd__(self, expr):
        super().__iadd__(expr)
        if not isinstance(expr, EmptyExpression):
            if isinstance(expr, LiteralValue) and self.variables == expr.variables:
                self.value += expr.value
            else:
                return Sum(self, expr)
        return self

    def __imul__(self, expr_or_n):
        super().__iadd__(expr_or_n)
        if not isinstance(expr_or_n, EmptyExpression):
            if isinstance(expr_or_n, LiteralValue):
                self.value *= expr_or_n.value
                self.variables += expr_or_n.variables
            elif isinstance(expr_or_n, int):
                self.value *= expr_or_n
            else:
                return Product(self, expr_or_n)
        return self

    def __neg__(self):
        return LiteralValue(-self.value, **self.variables.copy())

    def copy(self):
        return LiteralValue(self.value, **self.variables.copy())
    
    @property
    def degree(self):
        total = 0
        for deg in self.variables.values():
            total += deg
        return total
    
    def __repr__(self):
        txt = str(self.value) * (self.value != 1 or self.degree == 0)
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

    def __eq__(self, expr_or_n):
        if isinstance(expr_or_n, int):
            return self.degree == 0 and self.value == expr_or_n
        elif isinstance(expr_or_n, LiteralValue):
            return self.value == expr_or_n.value and self.variables == expr_or_n.variables
        return False

    def can_be_added_to(self, expr):
        if isinstance(expr, LiteralValue):
            return self.variables == expr.variables
        return False

a = LiteralValue(4, x=2)
b = LiteralValue(5, x=3)



