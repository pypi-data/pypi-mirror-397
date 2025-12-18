import pytest
from arctans import arccotan, arctan, is_irreducible, reduce, convert_rational, Rational
from utils import isclose

reducible = [3, 7, 8, 13, 17, 18, 21]


@pytest.mark.parametrize("n", range(1, 23))
def test_irreducible(n):
    assert is_irreducible(n) == (n not in reducible)


@pytest.mark.parametrize("coefficient", range(1, 20))
@pytest.mark.parametrize("a", range(1, 20))
def test_convert_rational_integer(coefficient, a):
    arctan_a = coefficient * arctan(a)
    converted = convert_rational(arctan_a)
    assert isclose(float(arctan_a), float(converted))
    for i, j in converted.terms:
        assert j.numerator == 1
        assert i != 0


@pytest.mark.parametrize("numerator", range(1, 20))
@pytest.mark.parametrize("denominator", range(1, 20))
def test_convert_rational(numerator, denominator):
    arctan_n = arctan(Rational(numerator, denominator))
    converted = convert_rational(arctan_n)
    assert isclose(float(arctan_n), float(converted))
    for i, j in converted.terms:
        assert j.numerator == 1
        assert i != 0


@pytest.mark.parametrize("n", reducible)
@pytest.mark.parametrize("c", [-2, -1, 1, 3, Rational(1, 2)])
def test_reduction(c, n):
    arctan_n = c * arctan(n)
    print(c, arctan(n))
    print(arctan_n)
    reduced = reduce(arctan_n)
    assert isclose(float(arctan_n), float(reduced))
    assert reduced.nterms > 1


@pytest.mark.parametrize("n", reducible)
def test_reduction_leads_to_irreducible(n):
    arctan_n = arctan(n)
    reduced = reduce(arctan_n)
    for _, i in reduced.terms:
        assert i == 0 or i == 1 or is_irreducible(1 / i)


@pytest.mark.parametrize("n", range(1, 300))
def test_reduction_nonzero_coefficients(n):
    arctan_n = arccotan(n)
    reduced = reduce(arctan_n)
    assert isclose(float(arctan_n), float(reduced))
    for i, _ in reduced.terms:
        assert i != 0
