import re
from dataclasses import dataclass
from itertools import chain, product
from pathlib import Path

EXAMPLE = """
467..114..
...*......
..35..633.
......#...
617*......
.....+.58.
..592.....
......755.
...$.*....
.664.598..
""".strip().splitlines()


@dataclass(frozen=True)
class Number:
    s_x: int
    e_x: int
    y: int
    val: int

    def neighbors(self, field):
        for x, y in chain(
            product(range(self.s_x - 1, self.e_x + 1),
                    (self.y - 1, self.y + 1)),
            [(self.s_x - 1, self.y), (self.e_x, self.y)]
        ):
            if -1 < x < len(field[0]) and -1 < y < len(field):
                yield (x, y)


def num_locs(lines):
    locs = []
    for y, row in enumerate(lines):
        for m in re.finditer(r'\d+', row):
            locs.append(
                Number(
                    s_x=m.start(),
                    e_x=m.end(),
                    y=y,
                    val=int(m.group(0)),
                )
            )
    return locs


def not_symbol_adjacent(field, nums):
    return [
        num for num in nums
        if all(field[y][x] == '.' for x, y in num.neighbors(field))
    ]


def test_not_symbol_adjacent():
    nas = not_symbol_adjacent(EXAMPLE, num_locs(EXAMPLE))
    assert [n.val for n in nas] == [114, 58]


def part1(lines):
    nums = num_locs(lines)
    adj = set(nums) - set(not_symbol_adjacent(lines, nums))
    return sum(n.val for n in adj)


def test_part1():
    assert part1(EXAMPLE) == 4361


def find_gear_adjacent(field, nums):
    gear_adjacent = []
    for num in nums:
        gears = [
            (x, y) for x, y in num.neighbors(field)
            if field[y][x] == '*'
        ]
        if gears:
            gear_adjacent.append((num, set(gears)))

    return gear_adjacent


def find_gear_pairs(field, gear_adjacent):
    for i in range(len(gear_adjacent)-1):
        num_i, gears_i = gear_adjacent[i]
        peers = []
        for j in range(i+1, len(gear_adjacent)):
            num_j, gears_j = gear_adjacent[j]
            if set(gears_i) & set(gears_j):
                peers.append(num_j)
        if len(peers) == 1:
            yield (num_i.val, peers[0].val)


def all_gear_pairs(field):
    nums = num_locs(field)
    gear_adjacent = find_gear_adjacent(field, nums)
    gear_pairs = find_gear_pairs(field, gear_adjacent)
    return gear_pairs


def test_all_gear_pairs():
    gear_pairs = all_gear_pairs(EXAMPLE)
    assert list(gear_pairs) == [(467, 35), (755, 598)]


def part2(lines):
    return sum(x * y for x, y in all_gear_pairs(lines))


def test_part2():
    assert part2(EXAMPLE) == 467835


if __name__ == '__main__':
    lines = Path("inputs/day03.txt").read_text().splitlines()
    print(part1(lines))
    print(part2(lines))
