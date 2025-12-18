import math
from arctans import arccotan, convert_rational, reduce
from utils import isclose


def test_convert_rational():
    a = convert_rational(arccotan(239))
    assert isclose(float(a), math.atan(1 / 239))


def test_machin_term2():
    a = reduce(arccotan(239))
    assert isclose(float(a), math.atan(1 / 239))
