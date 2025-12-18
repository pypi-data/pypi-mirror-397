"""Mathematical utility functions."""

from arctans.numbers import GaussianInteger, Integer, j

primes = [2]


def pfactors(n: int) -> list[Integer]:
    """Get list of all prime factors of n.

    Args:
        n: An integer

    Returns:
        A list of the prime factors of n, including factors multiple times when they appear more than once in the prime factorisation
    """
    out = []

    p = Integer(2)
    while n > 1:
        while n % p == 0:
            out.append(p)
            n //= p
        p += 1

    return out


def largest_pfactor(n: int | Integer) -> Integer:
    """Compute the largest prime factor of n.

    Args:
        n: An integer

    Returns:
        The largest prime factor of n
    """
    if n < 2:
        raise ValueError(f"Cannot find largest prime factor of {n}")
    n = int(n)
    i = 2
    while i < n:
        if n % i == 0:
            n //= i
        else:
            i += 1
    return Integer(n)


def is_prime(n: Integer | int) -> bool:
    """Check if an integer is prime.

    Args:
        n: An integer

    Returns:
        True if n is prime
    """
    global primes

    i = primes[-1]
    while primes[-1] < n:
        for p in primes:
            if i % p == 0:
                break
        else:
            primes.append(i)
        i += 1
    return n in primes


def is_irreducible(n: Integer | int) -> bool:
    """Check if arctan(n) is irreducible.

    An arctan is irreducible iff it cannot be written as a
    weighted sum of integer arccotangents, or equivalently
    arctan(n) is irreducible iff the largest prime factor of
    1 + n**2 is greater than or equal to 2*n.

    Args:
        n: An integer

    Returns:
        True if n is irreducible
    """
    return largest_pfactor(1 + n**2) >= 2 * n


def is_gaussian_prime(n: GaussianInteger) -> bool:
    """Check if n is a Gaussian prime.

    Args:
        n: An integer

    Returns:
        True if n is a Gaussian prime
    """
    if n.imag == 0 or n.real == 0:
        k = abs(n.real) + abs(n.imag)
        return k % 4 == 3 and is_prime(k)
    return is_prime(n.real**2 + n.imag**2)


def is_gaussian_unit(n: GaussianInteger) -> bool:
    """Check if n is a Gaussian unit.

    Args:
        n: An integer

    Returns:
        True if n is 1, -1, i or -i
    """
    return n in [GaussianInteger(1, 0), GaussianInteger(-1, 0), j, -j]


def complex_factorise(
    n: GaussianInteger,
    istart: int = 0,
) -> list[GaussianInteger]:
    """Factorise a Gaussian integer into Gaussian primes.

    Args:
        n: An integer

    Returns:
        A list of Gaussian primes
    """
    if is_gaussian_unit(n) or is_gaussian_prime(n):
        return [n]
    lim = int(abs(n)) + 1
    for re in range(istart, lim + 1):
        for im in range(-lim, lim + 1):
            m = GaussianInteger(re, im)
            if abs(m) > 1 and is_gaussian_prime(m) and n % m == 0:
                return [m] + complex_factorise(n // m, re)
    raise RuntimeError(f"Could not fund factor of non-prime number: {n}")
