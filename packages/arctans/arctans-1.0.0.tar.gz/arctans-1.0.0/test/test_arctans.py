from math import pi
from arctans import arctan, arccotan
from arctans.arctans import AbstractTerm
from utils import isclose


def test_simplify():
    s = arctan(5) + 2 * arctan(5)
    assert s.nterms == 1
    assert s.terms[0] == (3, 5)


def test_machins_formula():
    s = 16 * arccotan(5) - 4 * arccotan(239)
    assert isclose(float(s), pi)


def test_add():
    a = 16 * arccotan(5)
    b = -4 * arccotan(239)

    assert isinstance(a + b, AbstractTerm)

    assert isclose(float(a + b), pi)


def test_sub():
    a = 16 * arccotan(5)
    b = 4 * arccotan(239)

    assert isinstance(a - b, AbstractTerm)

    assert isclose(float(a - b), pi)


def test_multiply():
    a = 4 * arccotan(5) - arccotan(239)

    assert isinstance(4 * a, AbstractTerm)
    assert isinstance(a * 4, AbstractTerm)

    assert isclose(float(4 * a), pi)
    assert isclose(float(a * 4), pi)


def test_division():
    a = 64 * arccotan(5) - 16 * arccotan(239)

    assert isinstance(a / 4, AbstractTerm)

    assert isclose(float(a / 4), pi)
