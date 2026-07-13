from clinical_inference_workstation.doe.matrix import (
    build_fractional_factorial,
    build_full_factorial,
)


def test_should_build_full_factorial_as_product_of_factor_levels():
    factors = {"temperature": [1.0, 2.0, 3.0], "threshold": [0.4, 0.5]}

    cells = build_full_factorial(factors)

    assert len(cells) == 6


def test_should_carry_all_factor_keys_in_each_cell():
    factors = {"temperature": [1.0, 2.0], "threshold": [0.4, 0.5]}

    cells = build_full_factorial(factors)

    assert all(set(cell) == {"temperature", "threshold"} for cell in cells)


def test_should_include_expected_combination_in_full_factorial():
    factors = {"temperature": [1.0, 2.0], "threshold": [0.4, 0.5]}

    cells = build_full_factorial(factors)

    assert {"temperature": 2.0, "threshold": 0.4} in cells


def test_should_return_single_empty_cell_when_no_factors():
    assert build_full_factorial({}) == [{}]


def test_should_reduce_cell_count_for_fractional_factorial():
    factors = {"temperature": [1.0, 2.0, 3.0], "threshold": [0.4, 0.5]}
    full = build_full_factorial(factors)

    fraction = build_fractional_factorial(factors, fraction=2)

    assert len(fraction) < len(full)
    assert all(cell in full for cell in fraction)
