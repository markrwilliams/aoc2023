import itertools
from pathlib import Path
import pytest


EXAMPLE = """
0 3 6 9 12 15
1 3 6 10 15 21
10 13 16 21 30 45
""".strip().splitlines()


def ints_from_line(line):
    return [int(i) for i in line.strip().split()]


def stack_of_diffs(ints):
    stack = [ints]
    while any(stack[-1]):
        next_level = [b - a for a, b in itertools.pairwise(stack[-1])]
        stack.append(next_level)
    return stack


@pytest.mark.parametrize("seq,diffs", [
    ([0, 3, 6, 9, 12, 15],
     [[0, 3, 6, 9, 12, 15],
      [3, 3, 3, 3, 3],
      [0, 0, 0, 0]]),
    ([1, 3, 6, 10, 15, 21],
     [[1, 3, 6, 10, 15, 21],
      [2, 3, 4, 5, 6],
      [1, 1, 1, 1],
      [0, 0, 0]]),
    ([10, 13, 16, 21, 30, 45],
     [[10, 13, 16, 21, 30, 45],
      [3, 3, 5, 9, 15],
      [0, 2, 4, 6],
      [2, 2, 2],
      [0, 0]])
])
def test_stack_of_diffs(seq, diffs):
    assert stack_of_diffs(seq) == diffs


def next_in_sequence(diffs):
    for below, row in itertools.pairwise(reversed(diffs)):
        row.append(row[-1] + below[-1])
    return diffs[0][-1]


@pytest.mark.parametrize("seq,nis", [
    ([0, 3, 6, 9, 12, 15], 18),
    ([1, 3, 6, 10, 15, 21], 28),
    ([10, 13, 16, 21, 30, 45], 68),
])
def test_next_in_sequence(seq, nis):
    diffs = stack_of_diffs(seq)
    assert next_in_sequence(diffs) == nis


def part1(lines):
    return sum(
        next_in_sequence(
            stack_of_diffs(
                ints_from_line(line)))
        for line in lines
    )


def previous_in_sequence(diffs):
    for below, row in itertools.pairwise(reversed(diffs)):
        row.insert(0, row[0] - below[0])
    return diffs[0][0]


def test_previous_in_sequence():
    diffs = stack_of_diffs([10, 13, 16, 21, 30, 45])
    assert previous_in_sequence(diffs) == 5


def part2(lines):
    return sum(
        previous_in_sequence(
            stack_of_diffs(
                ints_from_line(line)))
        for line in lines
    )


def test_part2():
    assert part2(EXAMPLE) == 2


if __name__ == '__main__':
    lines = Path("inputs/day09.txt").read_text().splitlines()
    print(part1(lines))
    print(part2(lines))
