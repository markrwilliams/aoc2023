import re
from dataclasses import dataclass
from pathlib import Path

import pytest

EXAMPLE = """
seeds: 79 14 55 13

seed-to-soil map:
50 98 2
52 50 48

soil-to-fertilizer map:
0 15 37
37 52 2
39 0 15

fertilizer-to-water map:
49 53 8
0 11 42
42 0 7
57 7 4

water-to-light map:
88 18 7
18 25 70

light-to-temperature map:
45 77 23
81 45 19
68 64 13

temperature-to-humidity map:
0 69 1
1 0 69

humidity-to-location map:
60 56 37
56 93 4
""".strip().splitlines()


def parse_seeds(line_iter):
    seeds_line, _ = next(line_iter), next(line_iter)
    m = re.match(r'seeds:\s+((?:\d+\s*)+)', seeds_line)
    nums = m.group(1)
    return [int(i) for i in nums.split()]


def test_parse_seeds():
    seeds = parse_seeds(iter(EXAMPLE))
    assert seeds == [79, 14, 55, 13]


@dataclass
class Mapping:
    src: None
    dst: None

    def convert(self, num):
        if num not in self.src:
            return None
        offset = self.dst.start - self.src.start
        return num + offset


def convert(mappings, num):
    return next(
        (c for m in mappings if (c := m.convert(num)) is not None),
        num,
    )


def parse_maps(line_iter):
    all_mappings = {}
    for line in line_iter:
        m = re.match(r"([\w-]+)\s+map:", line)
        name = m.group(1)
        mappings = []
        for line in iter(line_iter.__next__, ""):
            start_dst, start_src, length = [int(i) for i in line.split()]
            dst = range(start_dst, start_dst + length)
            src = range(start_src, start_src + length)
            mappings.append(Mapping(src=src, dst=dst))
        all_mappings[name] = mappings
    return all_mappings


def test_pasre_mappings():
    expected = {
            "seed-to-soil": [
                Mapping(
                    src=range(98, 100), dst=range(50, 52),
                ),
                Mapping(
                    src=range(50, 98), dst=range(52, 100),
                )
            ]
         }
    actual = parse_maps(iter(EXAMPLE[2:5]))
    assert actual == expected


def parse(lines):
    line_iter = iter(lines)
    seeds = parse_seeds(line_iter)
    all_mappings = parse_maps(line_iter)
    return seeds, all_mappings


@pytest.mark.parametrize("seed,soil", [
    (79, 81),
    (14, 14),
    (55, 57),
    (13, 13),
])
def test_convert(seed, soil):
    ranges = parse_maps(iter(EXAMPLE[2:5]))['seed-to-soil']
    assert convert(ranges, seed) == soil


def seed_to_location(all_mappings, seed):
    num = seed
    for mappings in all_mappings.values():
        num = convert(mappings, num)
    return num


@pytest.mark.parametrize("seed,loc", [
    (79, 82),
    (14, 43),
    (55, 86),
    (13, 35),
])
def test_seed_to_location(seed, loc):
    _, all_mappings = parse(EXAMPLE)
    assert seed_to_location(all_mappings, seed) == loc


def part1(lines):
    seeds, all_mappings = parse(lines)
    locations = [seed_to_location(all_mappings, seed) for seed in seeds]
    return min(locations)


def test_part1():
    assert part1(EXAMPLE) == 35


if __name__ == '__main__':
    lines = Path("inputs/day05.txt").read_text().splitlines()
    print(part1(lines))


def part2_slow(lines):
    line_iter = iter(lines)
    seeds = parse_seeds(line_iter)
    seed_ranges = [range(int(start), int(stop))
                   for start, stop in zip(seeds[::2], seeds[1::2])]
    all_mappings = parse_maps(line_iter)
    locations = [seed_to_location(all_mappings, seed)
                 for seed_range in seed_ranges
                 for seed in seed_range]
    return min(locations)


def overlap(a, b):
    #   ____      ____
    #  |    |    |    |
    # a.s  a.e  b.s  b.e
    # return not (a[0] > b[-1] or a[-1] < b[0])
    # return (not (a[0] > b[-1])) and (not (a[-1] < b[0]))
    return (a[0] <= b[-1]) and (a[-1] >= b[0])


def convert_range(mapping, r):
    if not overlap(mapping.src, r):
        return
    # if there's an overlap, it falls into one of four cases:
    #
    # 1. the input range r ends after the start of the mapping range:
    #    |____r____|
    #         |____m____|
    # 2. the opposite (the mapping range ends after the start of input range r)
    #         |____r____|
    #    |____m____|
    # 3. r is inside m:
    #       |__r__|
    #    |_____m_____|
    # 4. m is inside r:
    #    |_____r_____|
    #       |__m__|
    #
    # case 3 is the easiest; we replace our input range's start and
    # stop with the corresponding numbers in the mapping range.
    #
    # case 1 requires us to split our input range r into two ranges:
    # r' = [r.start, m.start) and mr = [map(m.start), map(r.stop)):
    #    |____r____|
    #         |____m___|
    #    |_r'_|_mr_|
    #
    # case 2 is the same but in the other direction:
    # r' = [m.stop, r.stop) and mr = [map(r.start), map(m.stop-1)+1):
    # (note that m.stop can't be mapped because it's outside m!)
    #        |____r____|
    #   |____m____|
    #        |_mr_|_r'_|
    #
    # case 4 is 1 and 2 combined:
    #   |_________r_________|
    #         |   m   |
    #   |_r'__|__mr___|_r''_|
    #
    # that means case 1 is case 4 but with an empty r'', and case 2
    # with an empty r'. we'll rely on equivalence to return three
    # ranges, two of which might be empty.
    #
    # start and stop are the bounds of the overlap (mr).
    #
    # the overlap's start is either the input range's start (case 2)
    # or the mapping's start (case 1); we choose the largest because
    # one of three things is true:
    # 1. r.start comes later, cutting out mr from the rest of the mapping
    # 2. mapping's start comes later, splitting r' from mr
    # 3. the two starts are the same
    start = max(r.start, mapping.src.start)
    # similarly, we choose the minimum of the stops:
    # 1. r.stop comes earlier, delimiting mr from rest of the mapping
    # 2. mapping's stop comes earlier, marking the beginning of r'' from mr
    # 3. the two stops are the same
    stop = min(r.stop, mapping.src.stop)
    # before -- that is, r' -- is everything from r.start to the start
    # of the overlap; note that in cases 2 and 3 these are the same
    # and the range is empty
    before = range(r.start, start)
    # after -- that is, r'' -- is everything from the stop of the
    # overlap to r.stop; note that in cases 1 and 3 these are the same
    # and the range is empty
    after = range(stop, r.stop)
    # the overlap is the mapped start and stop
    overlapped = range(mapping.convert(start), mapping.convert(stop-1)+1)
    return before, overlapped, after


def convert_ranges(mappings, irange):
    for m in mappings:
        converted = convert_range(m, irange)
        if converted:
            yield from (r for r in converted if r)
            return
    yield from [irange]


def part_2(lines):
    seeds, all_mappings = parse(lines)
    ranges = [
        range(int(start), int(start) + int(stop))
        for start, stop in zip(seeds[::2], seeds[1::2])
    ]
    for mappings in all_mappings.values():
        ranges = [c for r in ranges for c in convert_ranges(mappings, r)]
    return min(r[0] for r in ranges)


def test_part2():
    assert part_2(EXAMPLE) == 46


if __name__ == '__main__':
    print(part_2(lines))
