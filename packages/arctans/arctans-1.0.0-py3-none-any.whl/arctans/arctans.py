"""Arctans."""

from arctans.numbers import AbstractNumber, Integer, RealNumber
from abc import abstractmethod
import math
from arctans.core import Representable


def _format_single_atan(a: AbstractNumber) -> str:
    """Format a single arctan."""
    if a.numerator == 1:
        return f"[{a.denominator}]"
    return f"arctan({a})"


class AbstractTerm(Representable):
    """Abstract term."""

    @property
    @abstractmethod
    def terms(self) -> list[tuple[AbstractNumber, AbstractNumber]]:
        """Return list of (coefficient, arctan) pairs."""

    @property
    @abstractmethod
    def term_dict(self) -> dict[AbstractNumber, AbstractNumber]:
        """Return dictionary {arctan: coefficient}."""

    def __eq__(self, other):
        if isinstance(other, AbstractTerm):
            return self.terms == other.terms
        return False

    def __neg__(self):
        return -1 * self

    def __add__(self, other):
        if isinstance(other, AbstractTerm):
            return ArctanSum(*self.terms, *other.terms)
        return NotImplemented

    def __iadd__(self, other):
        if not isinstance(other, AbstractTerm):
            return NotImplemented
        self = ArctanSum(*self.terms, *other.terms)
        return self

    def __sub__(self, other):
        if isinstance(other, AbstractTerm):
            return ArctanSum(*self.terms, *[(-i, j) for i, j in other.terms])
        else:
            return NotImplemented

    def __float__(self) -> float:
        out = 0.0
        for i, j in self.terms:
            out += float(i) * math.atan(float(j))
        return out

    def __mul__(self, other):
        return ArctanSum(*[(i * other, j) for i, j in self.terms])

    def __rmul__(self, other):
        return ArctanSum(*[(other * i, j) for i, j in self.terms])

    def __truediv__(self, other):
        return ArctanSum(*[(i / other, j) for i, j in self.terms])

    @property
    def nterms(self) -> int:
        """Number of terms."""
        return len(self.terms)

    def __hash__(self):
        return hash(self.__repr__())


class Zero(AbstractTerm):
    """Zero."""

    @property
    def terms(self) -> list[tuple[AbstractNumber, AbstractNumber]]:
        return []

    @property
    def term_dict(self) -> dict[AbstractNumber, AbstractNumber]:
        return {}

    def as_latex(self) -> str:
        return "0"

    def __str__(self) -> str:
        return "0"

    def __repr__(self) -> str:
        return "Zero()"

    def __float__(self) -> float:
        return 0.0


class Arctan(AbstractTerm):
    """A single arctan."""

    def __init__(self, arctan: AbstractNumber):
        """Initialise a single scaled arctan term.

        Args:
            coefficient: The coefficient that the arctan is scaled by
            arctan: The argument of the arctan

        """
        self._arctan = arctan

    @property
    def terms(self) -> list[tuple[AbstractNumber, AbstractNumber]]:
        return [(Integer(1), self._arctan)]

    @property
    def term_dict(self) -> dict[AbstractNumber, AbstractNumber]:
        return {self._arctan: Integer(1)}

    def as_latex(self) -> str:
        return f"\\arctan({self._arctan})"

    def __str__(self) -> str:
        return _format_single_atan(self._arctan)

    def __repr__(self) -> str:
        return f"Arctan({self._arctan})"


class ArctanSum(AbstractTerm):
    """The sum of some arctans."""

    def __init__(self, *terms: tuple[AbstractNumber, AbstractNumber]):
        """Initialise.

        Args:
            terms: A list of coefficient and arctan argument pairs
        """
        terms_dict: dict[AbstractNumber, AbstractNumber] = {}
        for c, a in terms:
            if isinstance(a, RealNumber) and a < 0:
                a *= -1
                c *= -1
            if a not in terms_dict:
                terms_dict[a] = Integer(0)
            terms_dict[a] += c
        self._terms = [(j, i) for i, j in terms_dict.items()]
        self._terms.sort(key=lambda i: 1 / abs(i[1]))
        self._terms = [i for i in self._terms if i[0] != 0]
        assert len(set([i[1] for i in self._terms])) == len([i[1] for i in self._terms])

    def as_latex(self) -> str:
        return " + ".join(
            ("" if i == 1 else f"{i}") + f"\\arctan({j})" for i, j in self._terms
        ).replace(
            "+ -",
            "- ",
        )

    def __repr__(self) -> str:
        return f"ArctanSum({self.__str__()})"

    def __str__(self) -> str:
        return " + ".join(f"{i}*{_format_single_atan(j)}" for i, j in self._terms).replace(
            "+ -",
            "- ",
        )

    @property
    def terms(self) -> list[tuple[AbstractNumber, AbstractNumber]]:
        return self._terms

    @property
    def term_dict(self) -> dict[AbstractNumber, AbstractNumber]:
        return {j: i for i, j in self._terms}


def arctan(a: AbstractNumber | int) -> AbstractTerm:
    """Symbolic arctangent.

    Args:
        a: The argument of the arctan

    Returns:
        arctan(a)

    """
    if isinstance(a, int):
        a = Integer(a)
    if isinstance(a, RealNumber) and a < 0:
        return -arctan(-a)
    if a == 0:
        return Zero()

    return Arctan(a)


def arccotan(a: AbstractNumber | int) -> AbstractTerm:
    """Symbolic arccotangent.

    Args:
        a: The argument of the arccotan

    Returns:
        arccotan(a)

    """
    if a == 0:
        return 2 * arctan(1)
    return arctan(Integer(1) / a)
