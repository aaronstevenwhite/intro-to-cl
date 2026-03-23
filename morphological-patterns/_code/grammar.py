from typing import Literal
from functools import lru_cache


class Rule:
    """A context-free grammar rule.

    Parameters
    ----------
    left_side : str
        The left-hand side variable.
    *right_side : str
        The right-hand side symbols.

    Attributes
    ----------
    left_side : str
        The left-hand side variable.
    right_side : tuple[str, ...]
        The right-hand side symbols.
    """

    def __init__(self, left_side: str, *right_side: str):
        self._left_side = left_side
        self._right_side = right_side

    def __repr__(self) -> str:
        """Return a string representation of the rule."""
        return self._left_side + ' -> ' + ' '.join(self._right_side)

    def to_tuple(self) -> tuple[str, tuple[str, ...]]:
        """Return the rule as a hashable tuple.

        Returns
        -------
        tuple[str, tuple[str, ...]]
            A pair of left side and right side.
        """
        return (self._left_side, self._right_side)

    def __hash__(self) -> int:
        return hash(self.to_tuple())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Rule):
            return NotImplemented
        return (self._left_side == other._left_side
                and self._right_side == other._right_side)

    @property
    def left_side(self) -> str:
        """The left-hand side variable."""
        return self._left_side

    @property
    def right_side(self) -> tuple[str, ...]:
        """The right-hand side symbols."""
        return self._right_side

    @property
    def is_unary(self) -> bool:
        """Whether the rule has exactly one symbol on the right side."""
        return len(self._right_side) == 1

    @property
    def is_binary(self) -> bool:
        """Whether the rule has exactly two symbols on the right side."""
        return len(self._right_side) == 2


type Mode = Literal["recognize", "parse"]


class ContextFreeGrammar:
    """A context-free grammar.

    Parameters
    ----------
    alphabet : set[str]
        The set of terminal symbols.
    variables : set[str]
        The set of nonterminal symbols.
    rules : set[Rule]
        The production rules.
    start_variable : str
        The start symbol.

    Attributes
    ----------
    alphabet : set[str]
        The set of terminal symbols.
    variables : set[str]
        The set of nonterminal symbols.
    start_variable : str
        The start symbol.
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

    def _validate_variables(self) -> None:
        """Check that alphabet and variables are disjoint and start variable is valid."""
        if self._alphabet & self._variables:
            raise ValueError('alphabet and variables must not share elements')

        if self._start_variable not in self._variables:
            raise ValueError('start variable must be in set of variables')

    def _validate_rules(self) -> None:
        """Validate the grammar rules (no-op in the base class)."""
        pass

    @property
    def alphabet(self) -> set[str]:
        """The set of terminal symbols."""
        return self._alphabet

    @property
    def variables(self) -> set[str]:
        """The set of nonterminal symbols."""
        return self._variables

    @lru_cache(2**10)
    def rules(self, left_side: str | None = None) -> set[Rule]:
        """Return the grammar rules, optionally filtered by left side.

        Parameters
        ----------
        left_side : str | None, default None
            If provided, return only rules with this left-hand side.

        Returns
        -------
        set[Rule]
            The matching rules.
        """
        if left_side is None:
            return self._rules
        else:
            return {rule for rule in self._rules
                    if rule.left_side == left_side}

    @property
    def start_variable(self) -> str:
        """The start symbol."""
        return self._start_variable

    @lru_cache(2**14)
    def parts_of_speech(self, word: str | None = None) -> set[str]:
        """Return parts of speech, optionally filtered to those generating a word.

        Parameters
        ----------
        word : str | None, default None
            If provided, return only parts of speech that generate this word.

        Returns
        -------
        set[str]
            The matching parts of speech.
        """
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
        """The nonterminals that head phrasal (non-lexical) rules."""
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
        """Find nonterminals that can be rewritten as the given right side.

        Parameters
        ----------
        *right_side : str
            The right-hand side symbols to match.

        Returns
        -------
        set[str]
            The nonterminals whose right side matches.
        """
        return {r.left_side for r in self._rules
                if r.right_side == tuple(right_side)}
