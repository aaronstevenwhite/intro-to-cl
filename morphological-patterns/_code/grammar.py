from typing import Literal, Optional
from functools import lru_cache


class Rule:
    """A context free grammar rule

    Parameters
    ----------
    left_side : str
    right_side : *str

    Attributes
    ----------
    left_side : str
    right_side : tuple(str)
    """

    def __init__(self, left_side, *right_side):
        self._left_side = left_side
        self._right_side = right_side

    def __repr__(self) -> str:
        return self._left_side + ' -> ' + ' '.join(self._right_side)

    def to_tuple(self) -> tuple[str, tuple[str, ...]]:
        return (self._left_side, self._right_side)

    def __hash__(self) -> int:
        return hash(self.to_tuple())

    def __eq__(self, other: 'Rule') -> bool:
        left_side_equal = self._left_side == other._left_side
        right_side_equal = self._right_side == other._right_side

        return left_side_equal and right_side_equal

    @property
    def left_side(self) -> str:
        return self._left_side

    @property
    def right_side(self) -> tuple[str, ...]:
        return self._right_side

    @property
    def is_unary(self) -> bool:
        return len(self._right_side) == 1

    @property
    def is_binary(self) -> bool:
        return len(self._right_side) == 2


Mode = Literal["recognize", "parse"]


class ContextFreeGrammar:
    """A context free grammar

    Parameters
    ----------
    alphabet : set(str)
    variables : set(str)
    rules : set(Rule)
    start_variable : str
    """

    parser_class = None

    def __init__(self, alphabet: set[str], variables: set[str],
                 rules: set[Rule], start_variable: str):
        self._alphabet = alphabet
        self._variables = variables
        self._rules = rules
        self._start_variable = start_variable

        self._validate_variables()
        self._validate_rules()

        if self.parser_class is not None:
            self._parser = self.parser_class(self)
        else:
            self._parser = None

    def _validate_variables(self):
        if self._alphabet & self._variables:
            raise ValueError('alphabet and variables must not share elements')

        if self._start_variable not in self._variables:
            raise ValueError('start variable must be in set of variables')

    def _validate_rules(self):
        pass

    @property
    def alphabet(self) -> set[str]:
        return self._alphabet

    @property
    def variables(self) -> set[str]:
        return self._variables

    @lru_cache(2**10)
    def rules(self, left_side: Optional[str] = None) -> set[Rule]:
        if left_side is None:
            return self._rules
        else:
            return {rule for rule in self._rules
                    if rule.left_side == left_side}

    @property
    def start_variable(self) -> str:
        return self._start_variable

    @lru_cache(2**14)
    def parts_of_speech(self, word: Optional[str] = None) -> set[str]:
        if word is None:
            return {rule.left_side for rule in self._rules
                    if rule.is_unary
                    if rule.right_side[0] in self._alphabet}
        else:
            return {rule.left_side for rule in self._rules
                    if rule.is_unary
                    if rule.right_side[0] == word}

    @property
    def phrase_variables(self) -> set[str]:
        try:
            return self._phrase_variables
        except AttributeError:
            self._phrase_variables = {
                rule.left_side for rule in self._rules
                if not rule.is_unary or
                rule.right_side[0] not in self._alphabet
            }
            return self._phrase_variables

    @lru_cache(2**15)
    def reduce(self, *right_side: str) -> set[str]:
        """The nonterminals that can be rewritten as right_side"""
        return {r.left_side for r in self._rules
                if r.right_side == tuple(right_side)}
