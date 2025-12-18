"""Generation of new formulae."""

from arctans.arctans import arctan, AbstractTerm
from arctans.numbers import Rational
from arctans.reduction import reduce
from typing import Sequence


def generate(
    known_formula: AbstractTerm | Sequence[AbstractTerm],
    *,
    min_denominator: int = 1,
    max_denominator: int = 100,
    min_numerator: int = 1,
    max_numerator: int = 1,
    max_terms: int | None = None,
    max_coefficient_denominator: int | None = None,
    printing: bool = False,
) -> list[AbstractTerm]:
    """Generate new formulae.

    Args:
        known_formula: Known formula or formulae that all have the same value
        min_numerator: The minimum numerator to use for arctan arguments
        max_numerator: The maximum numerator to use for arctan arguments
        min_denominator: The minimum denominator to use for arctan arguments
        max_denominator: The maximum denominator to use for arctan arguments
        max_terms: The maximum number of arctan terms to include in the new formulae
        max_coefficient_denominator: The maximum allowbale denominator to use in the
            coefficients in the new formulae
        printing: Print information about progress

    Returns:
        A list of new formulae that have the same value as the known formula(e)
    """
    if isinstance(known_formula, AbstractTerm):
        value = float(known_formula)
        known_formulae: Sequence[AbstractTerm] = [known_formula]
    else:
        value = float(known_formula[0])
        for i in known_formula[1:]:
            assert abs(float(i) - value) < 0.0001
        known_formulae = known_formula
    new_formulae = []
    for denominator in range(min_denominator, max_denominator + 1):
        for numerator in range(min_numerator, max_numerator + 1):
            if printing:
                print(numerator, denominator)
            a = arctan(Rational(numerator, denominator))
            zero = reduce(a) - a
            for c, t in zero.terms:
                for f in known_formulae:
                    if t in f.term_dict:
                        new_f = f - zero * f.term_dict[t] / c
                        if new_f in known_formulae or new_f in new_formulae:
                            continue
                        if max_terms is not None and len(new_f.terms) > max_terms:
                            continue
                        if (
                            max_coefficient_denominator is not None
                            and max(c.denominator for c, a in new_f.terms)
                            > max_coefficient_denominator
                        ):
                            continue
                        new_formulae.append(new_f)
    return new_formulae
