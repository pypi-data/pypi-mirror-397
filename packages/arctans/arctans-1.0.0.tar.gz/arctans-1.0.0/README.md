# arctans

arctans is a library for manipulating arctans to generate
[Machin-like formulae](https://machin-like.org) and other formulae involving arctans.

# Installing arctans
## Installing from PyPI using pip
The latest release of arctans can be installed by running:

```bash
pip3 install arctans
```

## Installing from source using pip
arctans can be installed by running:

```bash
pip3 install git+https://github.com/mscroggs/arctans.git
```

# Testing arctans
To run the arctans unit tests, clone the repository and run:

```bash
python3 -m pytest test/
```

# Using arctans
arctans can be used to represent arctans and sums of arctans symbolically
and generate arctan sums equivalent to a given set of sums.

For example, Machin's formula for pi (pi = 16arctan(1/5) - 4arctan(1/239)) can
be created with:

```python
from arctans import arctan, Rational

pi = 16 * arctan(Rational(1, 5)) - 4 * arctan(Rational(1, 239))
print(pi)
print(float(pi))
```

Or equivalently:

```python
from arctans import arccotan

pi = 16 * arccotan(5) - 4 * arccotan(239)
print(pi)
print(float(pi))
```

As arccotangents of integers commonly appear in formulae for pi, when printing
formulae represented using arctans, the shorthand notation `[n]` will be used
to represent `arccotan(n)`.

Once a formulae is expressed, new formulae that have the same value can be generated
using the `generate` function, for example:

```python
from arctans import arccotan, generate

pi = 16 * arccotan(5) - 4 * arccotan(239)

formulae = generate([pi])

for f in formulae:
    print(f)
```

This will print a number of different arctan sum formulae, including
`16*[4] + -16*[21] + -4*[239]` (ie pi = 16arctan(1/4) - 16arctan(1/21) - 4arctan(1/239)).

## Further documentation
More detailed documentation of the latest release version of arctans can be found on
[Read the Docs](https://arctans.readthedocs.io/en/latest/). A series of example uses
of arctans can be found in the [`demo` folder](demo/) or viewed on
[Read the Docs](https://arctans.readthedocs.io/en/latest/demos/index.html).

## Getting help
You can ask questions about using arctans by using [GitHub Discussions](https://github.com/mscroggs/arctans/discussions).
Bugs can be reported using the [GitHub issue tracker](https://github.com/mscroggs/arctans/issues).

# Contributing to arctans
## Reporting bugs and suggesting enhancements
If you find a bug in arctans and want to report it,
or if you want to suggest a new feature or an improvement of a current feature,
please open an issue on the [issue tracker](https://github.com/mscroggs/arctans/issues/new).

## Submitting a pull request
If you want to directly submit code to arctans, you can do this by forking the arctans repo, then submitting a pull request.
If you want to contribute, but are unsure where to start, have a look at the
[issues labelled "good first issue"](https://github.com/mscroggs/arctans/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22).

On opening a pull request, unit tests and ruff and mypy style checks will run. You can click on these in the pull request
to see where (if anywhere) there are errors in your code.

## Code of conduct
We expect all our contributors to follow [the Contributor Covenant](CODE_OF_CONDUCT.md). Any unacceptable
behaviour can be reported to Matthew (arctans@mscroggs.co.uk).

