"""Core base classes."""

from abc import ABC, abstractmethod


class Representable(ABC):
    """Object that can be represented as a string or as LaTeX."""

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass

    def __hash__(self):
        return hash(self.__repr__())

    @abstractmethod
    def as_latex(self) -> str:
        """Represent in LaTeX."""
