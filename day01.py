import re
from pathlib import Path

import pytest


def line_digits(line):
    digits = [c for c in line if c.isdigit()]
    return int(digits[0] + digits[-1])


@pytest.mark.parametrize("line,expected", [
    ("1abc2", 12),
    ("pqr3stu8vwx", 38),
    ("a1b2c3d4e5f", 15),
    ("treb7uchet", 77),
])
def test_line_digits(line, expected):
    assert line_digits(line) == expected


def part1(lines):
    return sum(line_digits(line) for line in lines)


if __name__ == '__main__':
    lines = Path("inputs/day01.txt").read_text().splitlines()
    print(part1(lines))


DIGITS = [
    'one',
    'two',
    'three',
    'four',
    'five',
    'six',
    'seven',
    'eight',
    'nine',
]


def all_line_digits(line):
    name_positions = [
        (m.start(), str(value))
        for value, digit in enumerate(DIGITS, 1)
        for m in re.finditer(digit, line)
    ]
    number_positions = [
        (i, str(c)) for i, c in enumerate(line) if c.isdigit()
    ]
    positions = sorted(name_positions + number_positions)
    return int(positions[0][1] + positions[-1][1])


INPUT = """two1nine
eightwothree
abcone2threexyz
xtwone3four
4nineeightseven2
zoneight234
7pqrstsixteen""".splitlines()


@pytest.mark.parametrize("line,expected",
                         list(zip(INPUT, [29, 83, 13, 24, 42, 14, 76])))
def test_all_line_digits(line, expected):
    assert all_line_digits(line) == expected


def test_all_line_digits_double_world():
    assert all_line_digits("threethree") == 33


if __name__ == '__main__':
    print(sum([all_line_digits(line) for line in lines]))
