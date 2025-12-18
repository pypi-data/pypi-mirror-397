"""Functions for reducing arctans."""

from functools import cache
import math
from arctans.primes import is_gaussian_prime, complex_factorise
from arctans.arctans import arccotan, arctan, Zero, AbstractTerm, Arctan
from arctans.numbers import j


@cache
def _convert_rational_single_arctan(a: Arctan) -> AbstractTerm:
    """Convert a rational arccotangent into a sum of integral arccotangents.

    Args:
        a: An arctan

    Returns:
        A sum of integral arccotangents
    """
    if a.terms[0][1].numerator == 1:
        return a
    beta = int(a.terms[0][1].numerator)
    alpha = int(a.terms[0][1].denominator)

    out = Zero()
    sign = 1
    while beta > 0:
        n = alpha // beta
        alpha, beta = alpha * n + beta, alpha % beta
        assert isinstance(a.terms[0][0] * arccotan(n), AbstractTerm)
        out += sign * a.terms[0][0] * arccotan(n)
        sign *= -1
    return out


def convert_rational(a: AbstractTerm) -> AbstractTerm:
    """Convert a rational arccotangent into a sum of integral arccotangents.

    Args:
        a: An arctan or sum of arctans

    Returns:
        A sum of integral arccotangents
    """
    if isinstance(a, Arctan):
        return _convert_rational_single_arctan(a)
    out = Zero()
    for c, arg in a.terms:
        at = arctan(arg)
        assert isinstance(at, Arctan)
        out += c * _convert_rational_single_arctan(at)
    return out


@cache
def _reduce_single_arctan(a: Arctan) -> AbstractTerm:
    """Express an arctan as a sum of irreducible integral arccotangents.

    Args:
        a: An arctan

    Returns:
        A sum of irreducible integral arccotangents
    """
    n = a.terms[0][1].denominator + j * a.terms[0][1].numerator
    if is_gaussian_prime(n):
        return a
    out = Zero()
    for f in complex_factorise(n):
        out += a.terms[0][0] * convert_rational(arctan(f.imag / f.real))

    return out


def reduce(a: AbstractTerm) -> AbstractTerm:
    """Express an arctan as a sum of irreducible integral arccotangents.

    Args:
        a: An arctan or sum of arctans

    Returns:
        A sum of irreducible integral arccotangents
    """
    out = Zero()
    for c, arg in a.terms:
        at = arctan(arg)
        assert isinstance(at, Arctan)
        out += c * _reduce_single_arctan(at)

    k = int(math.floor((float(a) - float(out)) * 4 / math.pi + 0.1))
    out += k * arctan(1)
    return out
