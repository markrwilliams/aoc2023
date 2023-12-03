from functools import reduce
from operator import mul
from pathlib import Path


def parse_reveals(raw_reveals):
    reveals = []
    for reveal in raw_reveals.split('; '):
        colors = dict.fromkeys(("red", "green", "blue"), 0)
        for color in reveal.split(', '):
            v, k = color.split()
            colors[k] = int(v)
        reveals.append(colors)
    return reveals


def parse_line(line):
    game, reveals = line.split(': ')
    _, gid = game.split()
    return (int(gid), parse_reveals(reveals))


PART1_EXAMPLE = """Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue
Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red
Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red
Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green""".splitlines()


def test_parse_line():
    line = PART1_EXAMPLE[0]
    assert parse_line(line) == (
        1, [
            {"red": 4, "green": 0, "blue": 3},
            {"red": 1, "green": 2, "blue": 6},
            {"red": 0, "green": 2, "blue": 0},
        ]
    )


def valid_game(reveals):
    constraint = {"red": 12, "green": 13, "blue": 14}
    return all(
        all(reveal[color] <= constraint[color] for color in constraint)
        for reveal in reveals
    )


def test_valid_game():
    games = [parse_line(line) for line in PART1_EXAMPLE]
    valid = [1, 2, 5]
    assert [gid for (gid, reveals) in games if valid_game(reveals)] == valid


def part1(lines):
    games = [parse_line(line) for line in lines]
    return sum(gid for (gid, reveals) in games if valid_game(reveals))


if __name__ == '__main__':
    lines = Path("inputs/day02.txt").read_text().splitlines()
    print(part1(lines))


def minimum_cubes(reveals):
    return {
        color: max(reveal[color] for reveal in reveals)
        for color in ("red", "green", "blue")
    }


def test_minimum_game():
    games = [parse_line(line) for line in PART1_EXAMPLE]
    minimums = [
        {"red": 4, "green": 2, "blue": 6},
        {"red": 1, "green": 3, "blue": 4},
        {"red": 20, "green": 13, "blue": 6},
        {"red": 14, "green": 3, "blue": 15},
        {"red": 6, "green": 3, "blue": 2},
    ]
    assert [minimum_cubes(reveals) for _, reveals in games] == minimums


def part2(lines):
    games = [parse_line(line) for line in lines]
    minimums = [
        reduce(mul, minimum_cubes(reveal).values(), 1) for (_, reveal) in games
    ]
    return sum(minimums)


def test_part2():
    assert part2(PART1_EXAMPLE) == 2286


if __name__ == '__main__':
    print(part2(lines))
