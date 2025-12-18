import pytest
from arctans.numbers import Integer, Rational, GaussianInteger, GaussianRational
from utils import isclose

options = [Integer(2), Rational(1, 2), GaussianInteger(3, 4), GaussianRational(1, 2, 3, 4)]


@pytest.mark.parametrize("a", options)
@pytest.mark.parametrize("b", options)
def test_add(a, b):
    assert isclose(complex(a + b), complex(a) + complex(b))


@pytest.mark.parametrize("a", options)
@pytest.mark.parametrize("b", options)
def test_sub(a, b):
    assert isclose(complex(a - b), complex(a) - complex(b))


@pytest.mark.parametrize("a", options)
@pytest.mark.parametrize("b", options)
def test_mul(a, b):
    assert isclose(complex(a * b), complex(a) * complex(b))


@pytest.mark.parametrize("a", options)
@pytest.mark.parametrize("b", options)
def test_div(a, b):
    print(a, b)
    assert isclose(complex(a / b), complex(a) / complex(b))
