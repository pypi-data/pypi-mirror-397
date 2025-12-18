from arctans import GaussianInteger
import pytest


def isclose(a, b, eps=1e-10):
    return abs(a - b) < eps


@pytest.mark.parametrize("a", [-3, 0, 2])
@pytest.mark.parametrize("b", [-3, 0, 2])
@pytest.mark.parametrize("c", [-3, 0, 2])
@pytest.mark.parametrize("d", [-3, 0, 2])
def test_add(a, b, c, d):
    w = GaussianInteger(a, b)
    z = GaussianInteger(c, d)
    assert isclose(complex(w + z), complex(w) + complex(z))


@pytest.mark.parametrize("a", [-3, 0, 2])
@pytest.mark.parametrize("b", [-3, 0, 2])
@pytest.mark.parametrize("c", [-3, 0, 2])
@pytest.mark.parametrize("d", [-3, 0, 2])
def test_sub(a, b, c, d):
    w = GaussianInteger(a, b)
    z = GaussianInteger(c, d)
    assert isclose(complex(w - z), complex(w) - complex(z))


@pytest.mark.parametrize("a", [-3, 0, 2])
@pytest.mark.parametrize("b", [-3, 0, 2])
@pytest.mark.parametrize("c", [-3, 0, 2])
@pytest.mark.parametrize("d", [-3, 0, 2])
def test_mult(a, b, c, d):
    w = GaussianInteger(a, b)
    z = GaussianInteger(c, d)
    assert isclose(complex(w * z), complex(w) * complex(z))


@pytest.mark.parametrize("a", [-3, 0, 2])
@pytest.mark.parametrize("b", [-3, 0, 2])
@pytest.mark.parametrize("c", [-3, 0, 2])
@pytest.mark.parametrize("d", [-3, 1, 2])
def test_mod(a, b, c, d):
    w = GaussianInteger(a, b)
    z = GaussianInteger(c, d)
    num = complex(w) * complex(z).conjugate()
    denom = int((complex(z) * complex(z).conjugate()).real)
    result = int(num.real) % denom + 1j * (int(num.imag) % denom)
    assert isclose(complex(w % z), result)


@pytest.mark.parametrize("a", [-3, 0, 2])
@pytest.mark.parametrize("b", [-3, 0, 2])
@pytest.mark.parametrize("c", [-3, 0, 2])
@pytest.mark.parametrize("d", [-3, 1, 2])
def test_division(a, b, c, d):
    w = GaussianInteger(a, b)
    z = GaussianInteger(c, d)
    assert isclose(complex(w / z), complex(w) / complex(z))


@pytest.mark.parametrize("a", [-3, 0, 2])
@pytest.mark.parametrize("b", [-3, 0, 2])
@pytest.mark.parametrize("c", [-3, 0, 2])
@pytest.mark.parametrize("d", [-3, 1, 2])
def test_integer_division(a, b, c, d):
    w = GaussianInteger(a, b)
    z = GaussianInteger(c, d)
    num = complex(w) * complex(z).conjugate()
    denom = int((complex(z) * complex(z).conjugate()).real)
    result = int(num.real) // denom + 1j * (int(num.imag) // denom)
    assert isclose(complex(w // z), result)


@pytest.mark.parametrize("a", [-3, 0, 2])
@pytest.mark.parametrize("b", [-3, 0, 2])
def test_abs(a, b):
    w = GaussianInteger(a, b)
    assert isclose(abs(w), abs(complex(w)))
