import re
from dataclasses import dataclass
from pathlib import Path

EXAMPLE = """
Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53
Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19
Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1
Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83
Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36
Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11
""".strip().splitlines()


@dataclass(frozen=True)
class Card:
    num: int
    winning: list[str]
    have: list[str]

    _PARSER = re.compile(
        r'Card +(?P<num>\d+): +'
        r'(?P<winning>\d+(?: +\d+)+) +\| +'
        r'(?P<card>\d+(?: +\d+)+)'
    )

    @classmethod
    def parse(cls, line):
        m = cls._PARSER.match(line)
        num = m.group('num')
        winning = m.group('winning')
        card = m.group('card')
        return cls(int(num), winning.split(), card.split())

    def wins(self):
        return set(self.winning) & set(self.have)


def test_wins():
    cards = [Card.parse(line) for line in EXAMPLE]
    wins = [c.wins() for c in cards]
    assert wins == [
        {'48', '83', '17', '86'},
        {'32', '61'},
        {'1', '21'},
        {'84'},
        set(),
        set(),
    ]


def part1(lines):
    cards = [Card.parse(line) for line in lines]
    wins = [c.wins() for c in cards]
    points = [2**(len(win)-1) if win else 0 for win in wins]
    return sum(points)


def test_part1():
    assert part1(EXAMPLE) == 13


if __name__ == '__main__':
    lines = Path('inputs/day04.txt').read_text().splitlines()
    print(part1(lines))


def card_count(lines):
    cards = [Card.parse(line) for line in lines]
    counts = dict.fromkeys([c.num for c in cards], 1)
    for card in cards:
        start = card.num + 1
        for i in range(start, start + len(card.wins())):
            counts[i] += counts[card.num]
    return counts


def test_card_count():
    assert card_count(EXAMPLE) == {
        1: 1,
        2: 2,
        3: 4,
        4: 8,
        5: 14,
        6: 1,
    }


def part2(lines):
    return sum(card_count(lines).values())


if __name__ == '__main__':
    print(part2(lines))
