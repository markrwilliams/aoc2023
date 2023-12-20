from itertools import cycle
from math import lcm
from pathlib import Path

from dataclasses import dataclass

EXAMPLE1 = """
RL

AAA = (BBB, CCC)
BBB = (DDD, EEE)
CCC = (ZZZ, GGG)
DDD = (DDD, DDD)
EEE = (EEE, EEE)
GGG = (GGG, GGG)
ZZZ = (ZZZ, ZZZ)
""".strip().splitlines()


EXAMPLE2 = """
LLR

AAA = (BBB, BBB)
BBB = (AAA, ZZZ)
ZZZ = (ZZZ, ZZZ)
""".strip().splitlines()


@dataclass
class Map:
    moves: str
    nodes: dict[str, tuple[str]]

    @classmethod
    def from_lines(cls, lines):
        lines_iter = iter(lines)

        moves = next(lines_iter)
        next(lines_iter)

        nodes = {}
        for line in lines_iter:
            node, _, left, right = line.split()
            nodes[node] = (left.strip('(,)'), right.strip('(,)'))

        return Map(moves, nodes)


def test_map_from_lines():
    m = Map.from_lines(EXAMPLE2)
    assert m.moves == 'LLR'
    assert m.nodes == {
        'AAA': ('BBB', 'BBB'),
        'BBB': ('AAA', 'ZZZ'),
        'ZZZ': ('ZZZ', 'ZZZ'),
    }


def part1(lines):
    m = Map.from_lines(lines)
    endless_moves = cycle(m.moves)
    cur = 'AAA'
    for i, move in enumerate(endless_moves):
        if cur == 'ZZZ':
            break
        left, right = m.nodes[cur]
        match move:
            case 'L':
                cur = left
            case 'R':
                cur = right
    return i


def test_part1():
    assert part1(EXAMPLE1) == 2
    assert part1(EXAMPLE2) == 6


if __name__ == '__main__':
    lines = Path("inputs/day08.txt").read_text().splitlines()
    print(part1(lines))


def part2(lines):
    # track count from each start to each end return the least common
    # multiple to account for overlaps (e.g. if ends = [2, 3, 6], then
    # we'll get to all ends at 2*3*6 = 36, but also sooner, at 6,
    # because we will end up on iteration 3 of 2 and iteration 2 of 3.
    m = Map.from_lines(lines)
    endless_moves = cycle(m.moves)
    curs = [node for node in m.nodes if node.endswith('A')]
    ends = [0] * len(curs)
    for i, move in enumerate(endless_moves):
        if all(ends):
            return lcm(*ends)
        for j, cur in enumerate(curs):
            if ends[j]:
                continue
            if cur.endswith('Z'):
                ends[j] = i

        match move:
            case 'L':
                curs = [m.nodes[cur][0] for cur in curs]
            case 'R':
                curs = [m.nodes[cur][1] for cur in curs]


EXAMPLE3 = """
LR

11A = (11B, XXX)
11B = (XXX, 11Z)
11Z = (11B, XXX)
22A = (22B, XXX)
22B = (22C, 22C)
22C = (22Z, 22Z)
22Z = (22B, 22B)
XXX = (XXX, XXX)
""".strip().splitlines()


def test_part2():
    assert part2(EXAMPLE3) == 6


if __name__ == '__main__':
    print(part2(lines))
