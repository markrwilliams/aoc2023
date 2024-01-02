import itertools
from pathlib import Path

import pytest

EXAMPLE = """
...#......
.......#..
#.........
..........
......#...
.#........
.........#
..........
.......#..
#...#.....
""".strip().splitlines()


def expand(image):
    output = []
    # double empty rows
    for line in image:
        output.append(list(line))
        if set(line) == {'.'}:
            output.append(list(line))

    for x in range(len(image[0]))[::-1]:
        values = set()
        for line in image:
            values.add(line[x])
        if values != {'.'}:
            continue
        for line in output:
            line.insert(x, '.')

    return output


EXPANDED = """
....#........
.........#...
#............
.............
.............
........#....
.#...........
............#
.............
.............
.........#...
#....#.......
""".strip().splitlines()


def test_expand():
    expected = [list(line) for line in EXPANDED]
    assert expand(EXAMPLE) == expected


def all_pairs(image):
    xys = [
        (x, y)
        for y, row in enumerate(image)
        for x, c in enumerate(row)
        if c == '#'
    ]
    return list(itertools.combinations(xys, 2))


def test_all_pairs():
    assert len(all_pairs(EXPANDED)) == 36


def taxi_cab_distance(start, end):
    sx, sy = start
    ex, ey = end
    return abs(sx - ex) + abs(sy - ey)


def test_taxi_cab_distance():
    start = (1, 6)
    end = (5, 11)
    assert taxi_cab_distance(start, end) == 9


def part1(lines):
    image = expand(lines)
    pairs = all_pairs(image)
    return sum(taxi_cab_distance(start, end) for start, end in pairs)


def test_part1():
    assert part1(EXAMPLE) == 374


if __name__ == '__main__':
    lines = Path('inputs/day11.txt').read_text().splitlines()
    print(part1(lines))


def find_galaxies(image):
    return [
        (x, y)
        for y, row in enumerate(image)
        for x, c in enumerate(row)
        if c == '#'
    ]


def expand_n(galaxies, image, n):
    empty_rows = [y for y, line in enumerate(image) if set(line) == {'.'}]
    empty_cols = [x for x in range(len(image[0]))
                  if set(image[y][x] for y in range(len(image))) == {'.'}]
    for empty_y in empty_rows[::-1]:
        galaxies = [
            (x, y + n - 1) if y > empty_y else (x, y) for x, y in galaxies
        ]
    for empty_x in empty_cols[::-1]:
        galaxies = [
            (x + n - 1, y) if x > empty_x else (x, y) for x, y in galaxies
        ]
    return galaxies


def part2(lines, n):
    galaxies = find_galaxies(lines)
    expanded_galaxies = expand_n(galaxies, lines, n)
    pairs = itertools.combinations(expanded_galaxies, 2)
    return sum(taxi_cab_distance(start, end) for start, end in pairs)


@pytest.mark.parametrize("n,total_dist", [
    (2, 374),
    (10, 1030),
    (100, 8410),
])
def test_expand_n(n, total_dist):
    assert part2(EXAMPLE, n) == total_dist


if __name__ == '__main__':
    print(part2(lines, 1_000_000))
