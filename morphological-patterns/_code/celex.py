"""Utilities for the CELEX English morphological lemma file."""

from __future__ import annotations

from dataclasses import dataclass
from os import PathLike
from pathlib import Path

import pyparsing as pp
from grammar import Rule

type Pathish = str | PathLike[str]


@dataclass(frozen=True, slots=True)
class CELEXEntry:
    """The fields used from one CELEX morphological lemma entry."""

    head: str
    struclab: str


@dataclass(frozen=True, slots=True)
class MorphTree:
    """A node in a CELEX morphological structure."""

    label: str
    children: tuple[MorphTree, ...] = ()
    form: str | None = None

    @property
    def rules(self) -> set[Rule]:
        """Return the CFG rules licensed by this subtree."""
        return set(self.rule_occurrences)

    @property
    def rule_occurrences(self) -> tuple[Rule, ...]:
        """Return every CFG rule occurrence in this subtree."""
        if self.form is not None:
            return (Rule(self.label, self.form),)

        local_rule = Rule(
            self.label,
            *(child.label for child in self.children),
        )
        return (local_rule,) + tuple(
            rule
            for child in self.children
            for rule in child.rule_occurrences
        )

    @property
    def morphemes(self) -> tuple[str, ...]:
        """Return the terminal forms from left to right."""
        if self.form is not None:
            return (self.form,)
        return tuple(
            form
            for child in self.children
            for form in child.morphemes
        )


def load_celex_entries(path: Pathish) -> list[CELEXEntry]:
    """Load heads and structure labels from ``eml.cd``.

    CELEX uses backslash-separated records. In the English
    morphological lemma file, field 1 is the head and field 21 is
    the morphological structure label.
    """
    entries: list[CELEXEntry] = []
    with Path(path).open(encoding="latin-1") as stream:
        for line in stream:
            fields = line.rstrip("\n").split("\\")
            if len(fields) <= 21:
                continue
            head, struclab = fields[1], fields[21]
            if head and struclab and struclab != "N":
                entries.append(CELEXEntry(head=head, struclab=struclab))
    return entries


_LABEL = pp.Suppress("[") + pp.Regex(r"[^\]]+") + pp.Suppress("]")
_FORM = pp.Regex(r"[^()\[\],]+")
_NODE = pp.Forward()
_LEAF = pp.Group(
    pp.Suppress("(") + _FORM + pp.Suppress(")") + _LABEL
)
_BRANCH = pp.Group(
    pp.Suppress("(")
    + _NODE
    + pp.ZeroOrMore(pp.Optional(pp.Suppress(",")) + _NODE)
    + pp.Suppress(")")
    + _LABEL
)
_NODE <<= _BRANCH | _LEAF


def parse_morph_tree(text: str) -> MorphTree:
    """Parse one CELEX ``StrucLab`` value."""
    parsed: object = _NODE.parse_string(text, parse_all=True)[0]
    if not isinstance(parsed, pp.ParseResults):
        raise TypeError("a CELEX structure must parse as a node")
    return _tree_from_parse_results(parsed)


def _tree_from_parse_results(parsed: pp.ParseResults) -> MorphTree:
    """Convert nested pyparsing results to an immutable tree."""
    if len(parsed) == 2:
        form, label = parsed
        if isinstance(form, str) and isinstance(label, str):
            return MorphTree(label=label.strip(), form=form.strip())

    label = parsed[-1]
    if not isinstance(label, str):
        raise TypeError("a CELEX branch must end in a string label")

    children: list[MorphTree] = []
    for child in parsed[:-1]:
        if not isinstance(child, pp.ParseResults):
            raise TypeError("a CELEX branch may contain only child nodes")
        children.append(_tree_from_parse_results(child))

    return MorphTree(
        label=label.strip(),
        children=tuple(children),
    )
