"""Numbers."""

from __future__ import annotations
import math
from abc import abstractmethod
from typing import Any
from arctans.core import Representable

try:
    from typing import Self  # type: ignore
except ImportError:
    from typing_extensions import Self


class AbstractNumber(Representable):
    """Base class for number."""

    @property
    @abstractmethod
    def real(self) -> RealNumber:
        """Real part."""

    @property
    @abstractmethod
    def imag(self) -> RealNumber:
        """Imaginary part."""

    @property
    @abstractmethod
    def numerator(self) -> AbstractNumber:
        """Numerator."""

    @property
    @abstractmethod
    def denominator(self) -> Integer:
        """Denominator."""

    @abstractmethod
    def conjugate(self) -> AbstractNumber:
        """Compute the complex conjugate."""

    @abstractmethod
    def __int__(self) -> int:
        pass

    @abstractmethod
    def __float__(self) -> float:
        pass

    @abstractmethod
    def __complex__(self) -> complex:
        pass

    @abstractmethod
    def _to_same_type(self, other: Any) -> Self:
        """Convert other to the same type as self."""

    @abstractmethod
    def _add(self, other: Self) -> AbstractNumber:
        """Add something of the same type to this."""

    @abstractmethod
    def _sub(self, other: Self) -> AbstractNumber:
        """Subtract something of the same type from this."""

    @abstractmethod
    def _mul(self, other: Self) -> AbstractNumber:
        """Multiply something of the same type by this."""

    @abstractmethod
    def _truediv(self, other: Self) -> AbstractNumber:
        """Divide this by something of the same type."""

    def _mod(self, other: Self) -> AbstractNumber:
        """Find the remainder when dividing this by something of the same type."""
        return NotImplemented

    def _floordiv(self, other: Self) -> AbstractNumber:
        """Find the remainder when dividing this by something of the same type."""
        return NotImplemented

    @abstractmethod
    def _eq(self, other: Self) -> bool:
        """Check if something of the same type is equal to this."""

    def _pow(self, other: int) -> AbstractNumber:
        """Raise to an integer power."""
        if other == 0:
            return Integer(1)
        elif other > 0:
            return _simplify_type(self._pow(other - 1) * self)
        else:  # other < 0
            return _simplify_type(self._pow(other + 1) / self)

    def __add__(self, other: Any):
        try:
            s, o = _as_common_type(self, other)
            return _simplify_type(s._add(o))
        except ValueError:
            return NotImplemented

    def __radd__(self, other: Any):
        try:
            s, o = _as_common_type(self, other)
            return _simplify_type(o._add(s))
        except ValueError:
            return NotImplemented

    def __sub__(self, other: Any):
        try:
            s, o = _as_common_type(self, other)
            return _simplify_type(s._sub(o))
        except ValueError:
            return NotImplemented

    def __rsub__(self, other: Any):
        try:
            s, o = _as_common_type(self, other)
            return _simplify_type(o._sub(s))
        except ValueError:
            return NotImplemented

    def __mul__(self, other: Any):
        try:
            s, o = _as_common_type(self, other)
            return _simplify_type(s._mul(o))
        except ValueError:
            return NotImplemented

    def __rmul__(self, other: Any):
        try:
            s, o = _as_common_type(self, other)
            return _simplify_type(o._mul(s))
        except ValueError:
            return NotImplemented

    def __neg__(self):
        return _simplify_type(-1 * self)

    def __truediv__(self, other: Any):
        try:
            s, o = _as_common_type(self, other)
            return _simplify_type(s._truediv(o))
        except ValueError:
            return NotImplemented

    def __rtruediv__(self, other: Any):
        try:
            s, o = _as_common_type(self, other)
            return _simplify_type(o._truediv(s))
        except ValueError:
            return NotImplemented

    def __mod__(self, other: Any):
        try:
            s, o = _as_common_type(self, other)
            return _simplify_type(s._mod(o))
        except ValueError:
            return NotImplemented

    def __rmod__(self, other: Any):
        try:
            s, o = _as_common_type(self, other)
            return _simplify_type(o._mod(s))
        except ValueError:
            return NotImplemented

    def __floordiv__(self, other: Any):
        try:
            s, o = _as_common_type(self, other)
            return _simplify_type(s._floordiv(o))
        except ValueError:
            return NotImplemented

    def __rfloordiv__(self, other: Any):
        try:
            s, o = _as_common_type(self, other)
            return _simplify_type(o._floordiv(s))
        except ValueError:
            return NotImplemented

    def __eq__(self, other) -> bool:
        try:
            s, o = _as_common_type(self, other)
            return s._eq(o)
        except ValueError:
            return NotImplemented

    def __pow__(self, other):
        try:
            return _simplify_type(self._pow(int(other)))
        except ValueError:
            return NotImplemented

    def __rpow__(self, other):
        try:
            return _simplify_type(other ** int(self))
        except ValueError:
            return NotImplemented

    def __iadd__(self, other):
        return self + other

    def __isub__(self, other):
        return self - other

    def __imul__(self, other):
        return self * other

    def __abs__(self):
        return math.sqrt(self.real**2 + self.imag**2)

    def __hash__(self):
        return hash(self.__repr__())


class RealNumber(AbstractNumber):
    """A real number."""

    @property
    def real(self) -> RealNumber:
        return self

    @property
    def imag(self) -> RealNumber:
        return Integer(0)

    def conjugate(self) -> AbstractNumber:
        return self

    def __lt__(self, other) -> bool:
        return int((self - other).numerator) < 0

    def __le__(self, other) -> bool:
        return int((self - other).numerator) <= 0

    def __gt__(self, other) -> bool:
        return int((self - other).numerator) > 0

    def __ge__(self, other) -> bool:
        return int((self - other).numerator) >= 0


class Integer(RealNumber):
    """An integer."""

    def __init__(self, i: int):
        """Initialise.

        Args:
            i: The integer
        """
        self._i = i

    def __str__(self):
        return f"{self._i}"

    def __repr__(self):
        return f"Integer({self._i})"

    def as_latex(self) -> str:
        return f"{self._i}"

    @property
    def numerator(self) -> AbstractNumber:
        return self

    @property
    def denominator(self) -> Integer:
        return Integer(1)

    def __int__(self) -> int:
        return self._i

    def __float__(self) -> float:
        return float(self._i)

    def __complex__(self) -> complex:
        return self._i + 0j

    def _to_same_type(self, other: Any) -> Integer:
        if isinstance(other, int):
            return Integer(other)
        if isinstance(other, Integer):
            return other
        raise ValueError(f"Could not convert {other} to integer")

    def _add(self, other: Self) -> AbstractNumber:
        return Integer(self._i + other._i)

    def _sub(self, other: Self) -> AbstractNumber:
        return Integer(self._i - other._i)

    def _mul(self, other: Self) -> AbstractNumber:
        return Integer(self._i * other._i)

    def _truediv(self, other: Self) -> AbstractNumber:
        return Rational(self._i, other._i)

    def _pow(self, other: int) -> AbstractNumber:
        return Integer(self._i**other)

    def _mod(self, other: Self) -> AbstractNumber:
        return Integer(self._i % other._i)

    def _floordiv(self, other: Self) -> AbstractNumber:
        return Integer(self._i // other._i)

    def _eq(self, other: Self) -> bool:
        return self._i == other._i

    def __abs__(self):
        return abs(self._i)

    def __hash__(self):
        return hash(self.__repr__())


class Rational(RealNumber):
    """A rational number."""

    def __init__(self, numerator: int, denominator: int):
        """Initialise.

        Args:
            numerator: The numerator
            denominator: The denominator
        """
        if denominator < 0:
            numerator *= -1
            denominator *= -1
        hcf = math.gcd(abs(numerator), abs(denominator))
        self._num = numerator // hcf
        self._den = denominator // hcf

    def as_latex(self) -> str:
        return f"\\frac{{{self._num}}}{{{self._den}}}"

    def __str__(self):
        return f"{self._num}/{self._den}"

    def __repr__(self):
        return f"Rational({self.__str__()})"

    @property
    def numerator(self) -> AbstractNumber:
        return Integer(self._num)

    @property
    def denominator(self) -> Integer:
        return Integer(self._den)

    def __int__(self) -> int:
        if self._den == 1:
            return self._num
        raise ValueError("Cannot convert rational number to integer")

    def __float__(self) -> float:
        return self._num / self._den

    def __complex__(self) -> complex:
        return float(self) + 0j

    def _to_same_type(self, other: Any) -> Rational:
        if isinstance(other, int):
            return Rational(other, 1)
        if isinstance(other, Integer):
            return Rational(int(other), 1)
        if isinstance(other, Rational):
            return other
        raise ValueError(f"Could not convert {other} to rational")

    def _add(self, other: Self) -> AbstractNumber:
        return Rational(
            self._num * other._den + self._den * other._num,
            self._den * other._den,
        )

    def _sub(self, other: Self) -> AbstractNumber:
        return Rational(
            self._num * other._den - self._den * other._num,
            self._den * other._den,
        )

    def _mul(self, other: Self) -> AbstractNumber:
        return Rational(
            self._num * other._num,
            self._den * other._den,
        )

    def _truediv(self, other: Self) -> AbstractNumber:
        return Rational(
            self._num * other._den,
            self._den * other._num,
        )

    def _pow(self, other: int) -> AbstractNumber:
        return Rational(
            self._num**other,
            self._den**other,
        )

    def _eq(self, other: Self) -> bool:
        return self._num == other._num and self._den == other._den

    def __abs__(self):
        return abs(float(self))


class GaussianInteger(AbstractNumber):
    """A Gaussian integer."""

    def __init__(self, re: int, im: int):
        """Initialise.

        Args:
            re: The real part
            im: The imaginary part
        """
        self._re = re
        self._im = im

    def __str__(self):
        return f"{self._re}+{self._im}j"

    def __repr__(self):
        return f"GaussianInteger({self._re}+{self._im}j)"

    @property
    def real(self) -> RealNumber:
        return Integer(self._re)

    @property
    def imag(self) -> RealNumber:
        return Integer(self._im)

    def conjugate(self) -> AbstractNumber:
        return GaussianInteger(self._re, -self._im)

    def as_latex(self) -> str:
        return f"{self._re}+{self._im}\\mathrm{{i}}"

    @property
    def numerator(self) -> AbstractNumber:
        return self

    @property
    def denominator(self) -> Integer:
        return Integer(1)

    def __int__(self) -> int:
        if self._im == 0:
            return self._re
        raise ValueError("Cannot convert complex number to integer")

    def __float__(self) -> float:
        if self._im == 0:
            return float(self._re)
        raise ValueError("Cannot convert complex number to integer")

    def __complex__(self) -> complex:
        return self._re + 1j * self._im

    def _to_same_type(self, other: Any) -> GaussianInteger:
        if isinstance(other, int):
            return GaussianInteger(other, 0)
        if isinstance(other, Integer):
            return GaussianInteger(int(other), 0)
        if isinstance(other, GaussianInteger):
            return other
        raise ValueError(f"Could not convert {other} to Gaussian integer")

    def _add(self, other: Self) -> AbstractNumber:
        return GaussianInteger(self._re + other._re, self._im + other._im)

    def _sub(self, other: Self) -> AbstractNumber:
        return GaussianInteger(self._re - other._re, self._im - other._im)

    def _mul(self, other: Self) -> AbstractNumber:
        return GaussianInteger(
            self._re * other._re - self._im * other._im,
            self._re * other._im + self._im * other._re,
        )

    def _truediv(self, other: Self) -> AbstractNumber:
        num = self * other.conjugate()
        den = other * other.conjugate()
        return GaussianRational(int(num.real), int(den), int(num.imag), int(den))

    def _mod(self, other: Self) -> AbstractNumber:
        num = self * other.conjugate()
        den = other * other.conjugate()
        return GaussianInteger(int(num.real % den), int(num.imag % den))

    def _floordiv(self, other: Self) -> AbstractNumber:
        num = self * other.conjugate()
        den = other * other.conjugate()
        return GaussianInteger(int(num.real // den), int(num.imag // den))

    def _eq(self, other: Self) -> bool:
        return self._re == other._re and self._im == other._im


class GaussianRational(AbstractNumber):
    """A Gaussian rational."""

    def __init__(self, re_numerator: int, re_denominator, im_numerator: int, im_denominator: int):
        """Initialise.

        Args:
            re_numerator: The numerator of the real part
            re_denominator: The denominator of the real part
            im_numerator: The numerator of the imaginary part
            im_denominator: The denominator of the imaginary part
        """
        if re_denominator < 0:
            re_numerator *= -1
            re_denominator *= -1
        if im_denominator < 0:
            im_numerator *= -1
            im_denominator *= -1
        hcf = math.gcd(abs(re_numerator), abs(re_denominator))
        self._re_num = re_numerator // hcf
        self._re_den = re_denominator // hcf
        hcf = math.gcd(abs(im_numerator), abs(im_denominator))
        self._im_num = im_numerator // hcf
        self._im_den = im_denominator // hcf

    def __str__(self):
        return f"{self._re_num}/{self._re_den} + {self._im_num}j/{self._im_den}"

    def __repr__(self):
        return f"GaussianRational({self})"

    @property
    def real(self) -> RealNumber:
        return Rational(self._re_num, self._re_den)

    @property
    def imag(self) -> RealNumber:
        return Rational(self._im_num, self._im_den)

    def as_latex(self) -> str:
        return f"\\frac{{{self._re_num}}}{{{self._re_den}}}+\\frac{{{self._im_num}}}{{{self._im_den}}}\\mathrm{{i}}"

    def conjugate(self) -> AbstractNumber:
        return GaussianRational(self._re_num, self._re_den, -self._im_num, self._im_den)

    @property
    def numerator(self) -> AbstractNumber:
        d = int(self.denominator)
        return GaussianInteger(
            self._re_num * d // self._re_den,
            self._im_num * d // self._im_den,
        )

    @property
    def denominator(self) -> Integer:
        return Integer(math.lcm(self._re_den, self._im_den))

    def __int__(self) -> int:
        if self._im_num == 0 and self._re_den == 1:
            return self._re_num
        raise ValueError("Cannot convert complex number to integer")

    def __float__(self) -> float:
        if self._im_num == 0:
            return self._re_num / self._re_den
        raise ValueError("Cannot convert complex number to integer")

    def __complex__(self) -> complex:
        return self._re_num / self._re_den + 1j * self._im_num / self._im_den

    def _to_same_type(self, other: Any) -> GaussianRational:
        if isinstance(other, int):
            return GaussianRational(other, 1, 0, 1)
        if isinstance(other, Integer):
            return GaussianRational(int(other), 1, 0, 1)
        if isinstance(other, Rational):
            return GaussianRational(int(other.numerator), int(other.denominator), 0, 1)
        if isinstance(other, GaussianInteger):
            return GaussianRational(int(other.real), 1, int(other.imag), 1)
        if isinstance(other, GaussianRational):
            return other
        raise ValueError(f"Could not convert {other} to Gaussian rational")

    def _add(self, other: Self) -> AbstractNumber:
        re = self.real + other.real
        im = self.imag + other.imag
        return GaussianRational(
            int(re.numerator), int(re.denominator), int(im.numerator), int(im.denominator)
        )

    def _sub(self, other: Self) -> AbstractNumber:
        re = self.real - other.real
        im = self.imag - other.imag
        return GaussianRational(
            int(re.numerator), int(re.denominator), int(im.numerator), int(im.denominator)
        )

    def _mul(self, other: Self) -> AbstractNumber:
        re = self.real * other.real - self.imag * other.imag
        im = self.real * other.imag + self.imag * other.real
        return GaussianRational(
            int(re.numerator), int(re.denominator), int(im.numerator), int(im.denominator)
        )

    def _truediv(self, other: Self) -> AbstractNumber:
        num = self * other.conjugate()
        den = other * other.conjugate()
        re = num.real / den
        im = num.imag / den
        return GaussianRational(
            int(re.numerator), int(re.denominator), int(im.numerator), int(im.denominator)
        )

    def _eq(self, other: Self) -> bool:
        return self.real == other.real and self.imag == other.imag


def _simplify_type(i: AbstractNumber) -> AbstractNumber:
    """Convert i to a simpler type if possible."""
    if isinstance(i, Rational):
        if i.denominator == 1:
            return _simplify_type(i.numerator)
    if isinstance(i, GaussianInteger):
        if i.imag == 0:
            return _simplify_type(i.real)
    if isinstance(i, GaussianRational):
        if i.imag == 0:
            return _simplify_type(i.real)
        if i.denominator == 1:
            return _simplify_type(i.numerator)
    return i


def _as_common_type(a: AbstractNumber, b: Any) -> tuple[AbstractNumber, AbstractNumber]:
    """Convert a and b to the same type."""
    try:
        return a, a._to_same_type(b)
    except ValueError:
        pass
    if isinstance(b, AbstractNumber):
        try:
            return b._to_same_type(a), b
        except ValueError:
            pass
    i = GaussianRational(1, 2, 1, 2)
    try:
        return i._to_same_type(a), i._to_same_type(b)
    except ValueError:
        raise ValueError(f"Could not find common type for {a} and {b}")


j = GaussianInteger(0, 1)
zero = Integer(0)
one = Integer(1)
