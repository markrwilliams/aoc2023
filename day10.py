from dataclasses import dataclass
from pathlib import Path
from typing import Union

import pytest


def example(s):
    return s.strip().splitlines()


EXAMPLE1 = example("""
.....
.S-7.
.|.|.
.L-J.
.....
""")

EXAMPLE2 = example("""
-L|F7
7S-7|
L|7||
-L-J|
L|-JF
""")

EXAMPLE3 = example("""
7-F7-
.FJ|7
SJLL7
|F--J
LJ.LJ
""")

EXAMPLE4 = example("""
..F7.
.FJ|.
SJ.L7
|F--J
LJ...
""")


NEIGHBORS = {
    "n": (0, -1),
    'e': (1, 0),
    'w': (-1, 0),
    's': (0, 1),
}

MIRROR = {
    'n': 's',
    'e': 'w',
    'w': 'e',
    's': 'n',
}

CONNECTIONS = {
    '|': {'n', 's'},
    '-': {'e', 'w'},
    'L': {'n', 'e'},
    'J': {'n', 'w'},
    '7': {'s', 'w'},
    'F': {'s', 'e'},
    '.': {},
    'S': {'n', 'e', 'w', 's'},
}


@dataclass
class Tile:
    t: str
    x: int
    y: int
    n: Union['Tile', None]
    e: Union['Tile', None]
    w: Union['Tile', None]
    s: Union['Tile', None]

    def neighbors(self):
        return CONNECTIONS[self.t]

    def connect(self, tiles):
        for direction in self.neighbors():
            dx, dy = NEIGHBORS[direction]
            nx, ny = self.x + dx, self.y + dy
            if -1 < nx < len(tiles[0]) and -1 < ny < len(tiles):
                peer = tiles[ny][nx]
                if direction in {MIRROR[n] for n in peer.neighbors()}:
                    setattr(self, direction, peer)

    def connected(self):
        return [
            neighbor
            for direction
            in self.neighbors()
            if (neighbor := getattr(self, direction))
        ]


def parse_map(lines):
    tiles = []
    for y, line in enumerate(lines):
        tiles.append([])
        row = tiles[-1]
        for x, item in enumerate(line):
            row.append(Tile(item, x, y, None, None, None, None))

    start = None
    for row in tiles:
        for tile in row:
            if tile.t == 'S':
                start = tile
            tile.connect(tiles)

    return start, tiles


def test_parse_map():
    start, tiles = parse_map(EXAMPLE1)
    assert tiles[1][1] is start
    assert start.n is None

    assert start.e is tiles[1][2]
    assert start.e.t == '-'

    assert start.w is None

    assert start.s is tiles[2][1]
    assert start.s.t == '|'


def count_steps(start):
    seen = set([(start.x, start.y)])
    counts = set()
    queue = [(1, n) for n in start.connected()]
    while queue:
        count, tile = queue.pop(0)
        loc = (tile.x, tile.y)
        seen.add(loc)
        counts.add(count)
        queue.extend((count + 1, n) for n in tile.connected()
                     if (n.x, n.y) not in seen)
    return max(counts)


def part1(lines):
    start, _ = parse_map(lines)
    return count_steps(start)


@pytest.mark.parametrize("ex,count", [
    (EXAMPLE1, 4),
    (EXAMPLE2, 4),
    (EXAMPLE3, 8),
    (EXAMPLE4, 8),
])
def test_part1(ex, count):
    assert part1(ex) == count


if __name__ == '__main__':
    lines = Path('inputs/day10.txt').read_text().splitlines()
    print(part1(lines))


def trace_polygon(start):
    seen = {(start.x, start.y)}
    queue = start.connected()
    while queue:
        tile = queue.pop(0)
        loc = (tile.x, tile.y)
        seen.add(loc)
        queue.extend(n for n in tile.connected() if (n.x, n.y) not in seen)
    return seen


def count_inside(polygon, tiles):
    # Verticals:
    # |
    # F-*J
    # L-*7
    count = 0
    for y, row in enumerate(tiles):
        ends_line = None
        is_odd = False
        for x, tile in enumerate(row):
            if (x, y) not in polygon:
                if is_odd:
                    count += 1
                continue
            match tile.t:
                case '|':
                    is_odd ^= True
                case 'L':
                    ends_line = '7'
                case 'F':
                    ends_line = 'J'
                case '7' if ends_line == '7':
                    ends_line = None
                    is_odd ^= True
                case 'J' if ends_line == 'J':
                    ends_line = None
                    is_odd ^= True
                case '-' if ends_line:
                    continue
                case _:
                    ends_line = None
    return count


def part2(lines):
    start, tiles = parse_map(lines)
    polygon = trace_polygon(start)
    start_neighbors = {d for d in "news" if getattr(start, d)}
    start.t = next(t for t, ns in CONNECTIONS.items() if start_neighbors == ns)
    return count_inside(polygon, tiles)


EXAMPLE2_1 = example("""
...........
.S-------7.
.|F-----7|.
.||.....||.
.||.....||.
.|L-7.F-J|.
.|..|.|..|.
.L--J.L--J.
...........
""")


EXAMPLE2_2 = example("""
..........
.S------7.
.|F----7|.
.||....||.
.||....||.
.|L-7F-J|.
.|..||..|.
.L--JL--J.
..........
""")


EXAMPLE2_3 = example("""
.F----7F7F7F7F-7....
.|F--7||||||||FJ....
.||.FJ||||||||L7....
FJL7L7LJLJ||LJ.L-7..
L--J.L7...LJS7F-7L7.
....F-J..F7FJ|L7L7L7
....L7.F7||L7|.L7L7|
.....|FJLJ|FJ|F7|.LJ
....FJL-7.||.||||...
....L---J.LJ.LJLJ...
""")


EXAMPLE2_4 = example("""
FF7FSF7F7F7F7F7F---7
L|LJ||||||||||||F--J
FL-7LJLJ||||||LJL-77
F--JF--7||LJLJ7F7FJ-
L---JF-JLJ.||-FJLJJ7
|F|F-JF---7F7-L7L|7|
|FFJF7L7F-JF7|JL---7
7-L-JL7||F7|L7F-7F7|
L.L7LFJ|||||FJL7||LJ
L7JLJL-JLJLJL--JLJ.L
""")


@pytest.mark.parametrize("ex,count", [
    (EXAMPLE2_1, 4),
    (EXAMPLE2_2, 4),
    (EXAMPLE2_3, 8),
    (EXAMPLE2_4, 10)
])
def test_part2(ex, count):
    assert part2(ex) == count


if __name__ == '__main__':
    print(part2(lines))
