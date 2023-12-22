from dataclasses import dataclass
from functools import reduce
from operator import mul
from pathlib import Path

EXAMPLE = """
Time:      7  15   30
Distance:  9  40  200
""".strip().splitlines()


@dataclass
class Race:
    time: int
    distance: int


def parse_races(lines):
    name, _, times = lines[0].partition(':')
    assert name == 'Time', name
    name, _, distances = lines[1].partition(':')
    assert name == 'Distance', name
    return [
        Race(time=int(time),
             distance=int(distance))
        for time, distance in zip(times.split(), distances.split())
    ]


def test_parse_races():
    parsed = parse_races(EXAMPLE)
    assert parsed == [
        Race(time=7, distance=9),
        Race(time=15, distance=40),
        Race(time=30, distance=200),
    ]


def distance_for_hold(time):
    return [
        hold * (time - hold)
        for hold in range(1, time)
    ]


def test_distance_for_hold():
    distances = distance_for_hold(7)
    assert distances == [6, 10, 12, 12, 10, 6]


def ways_to_win(race):
    distances = distance_for_hold(race.time)
    return sum(1 for d in distances if d > race.distance)


def test_ways_to_win():
    race = Race(time=7, distance=9)
    assert ways_to_win(race) == 4


def part1(lines):
    races = parse_races(lines)
    wins = [ways_to_win(race) for race in races]
    return reduce(mul, wins)


def test_part1():
    assert part1(EXAMPLE) == 288


if __name__ == '__main__':
    lines = Path("inputs/day06.txt").read_text().splitlines()
    print(part1(lines))


def parse_race(lines):
    name, _, times = lines[0].partition(':')
    assert name == 'Time'
    name, _, distances = lines[1].partition(':')
    assert name == 'Distance'
    time = int("".join(times.split()))
    distance = int("".join(distances.split()))
    return Race(time=int(time), distance=int(distance))


def test_parse_race():
    race = parse_race(EXAMPLE)
    assert race == Race(time=71530, distance=940200)


def fast_ways_to_win(race):
    first_hold = None
    for first_hold in range(race.time//2):
        if first_hold * (race.time - first_hold) > race.distance:
            break
    if first_hold is None:
        raise ValueError(race)
    last_hold = race.time - first_hold
    return (last_hold - first_hold) + 1


def test_fast_ways_to_win():
    races = parse_races(EXAMPLE)
    for race in races:
        assert fast_ways_to_win(race) == ways_to_win(race)


def part2(lines):
    race = parse_race(lines)
    ways = fast_ways_to_win(race)
    return ways


def test_part2():
    assert part2(EXAMPLE) == 71503


if __name__ == '__main__':
    print(part2(lines))
