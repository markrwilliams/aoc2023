from collections import Counter
from dataclasses import dataclass, field, replace
from enum import Enum
from functools import total_ordering
from pathlib import Path

import pytest

CARD_RANKS = '23456789TJQKA'
JOKER_CARD_RANKS = 'J23456789TQKA'


class HandType(Enum):
    HIGH_CARD = Counter([1, 1, 1, 1, 1])
    ONE_PAIR = Counter([2, 1, 1, 1])
    TWO_PAIR = Counter([2, 2, 1])
    THREE_OF_A_KIND = Counter([3, 1, 1])
    FULL_HOUSE = Counter([3, 2])
    FOUR_OF_A_KIND = Counter([4, 1])
    FIVE_OF_A_KIND = Counter([5])


@dataclass
@total_ordering
class Hand:
    cards: str
    counts: Counter[int, int]
    type: HandType
    ranks: str = field(default=CARD_RANKS)

    @classmethod
    def from_cards(cls, cards):
        spread = Counter(cards)
        counts = Counter(spread.values())
        return cls(cards, counts, HandType(counts))

    def __lt__(self, other):
        return (
            list(HandType).index(self.type),
            [self.ranks.index(c) for c in self.cards],
        ) < (
            list(HandType).index(other.type),
            [self.ranks.index(c) for c in other.cards]
        )


EXAMPLE_HANDS = {
    HandType.FIVE_OF_A_KIND: 'AAAAA',
    HandType.FOUR_OF_A_KIND: 'AA8AA',
    HandType.FULL_HOUSE: '23332',
    HandType.THREE_OF_A_KIND: 'TTT98',
    HandType.TWO_PAIR: '23432',
    HandType.ONE_PAIR: 'A23A4',
    HandType.HIGH_CARD: '23456',
}


@pytest.mark.parametrize('hand_type', HandType)
def test_hand(hand_type):
    others = set(HandType) - {hand_type}
    for other in others:
        other_hand = Hand.from_cards(EXAMPLE_HANDS[other])
        assert other_hand.type != hand_type, other_hand
    hand = Hand.from_cards(EXAMPLE_HANDS[hand_type])
    assert hand.type == hand_type, hand


def test_sort_type():
    hands = [
        EXAMPLE_HANDS[HandType.THREE_OF_A_KIND],
        EXAMPLE_HANDS[HandType.FULL_HOUSE],
    ]
    assert sorted(hands) == [
        EXAMPLE_HANDS[HandType.FULL_HOUSE],
        EXAMPLE_HANDS[HandType.THREE_OF_A_KIND],
    ]


@pytest.mark.parametrize("weaker,stronger,type", [
    (Hand.from_cards('2AAAA'),
     Hand.from_cards('33332'),
     HandType.FOUR_OF_A_KIND),
    (Hand.from_cards('77788'),
     Hand.from_cards('77888'),
     HandType.FULL_HOUSE)
])
def sort_cards(weaker, stronger, type):
    assert weaker.type == type
    assert stronger.type == type
    assert sorted([stronger, weaker]) == [weaker, stronger]


EXAMPLE = """
32T3K 765
T55J5 684
KK677 28
KTJJT 220
QQQJA 483
""".strip().splitlines()


def parse_hands_and_bids(lines):
    cards_to_bids = {}
    for line in lines:
        cards, bid = line.split()
        cards_to_bids[cards] = int(bid)
    hands = [Hand.from_cards(card) for card in cards_to_bids]
    return cards_to_bids, hands


def rank_and_bid(cards_to_bids, hands):
    return [
        (hand.cards, i, cards_to_bids[hand.cards])
        for i, hand in enumerate(sorted(hands), 1)
    ]


def test_rank_and_bid():
    cards_to_bids, hands = parse_hands_and_bids(EXAMPLE)
    assert rank_and_bid(cards_to_bids, hands) == [
        ('32T3K', 1, 765),
        ('KTJJT', 2, 220),
        ('KK677', 3, 28),
        ('T55J5', 4, 684),
        ('QQQJA', 5, 483),
    ]


def winnings(lines, handify=None):
    cards_to_bids, hands = parse_hands_and_bids(lines)
    if callable(handify):
        hands = handify(hands)
    return sum(
        rank * bid
        for _, rank, bid in
        rank_and_bid(cards_to_bids, hands)
    )


def part1(lines):
    return winnings(lines)


def test_part1():
    assert part1(EXAMPLE) == 6440


if __name__ == '__main__':
    lines = Path('inputs/day07.txt').read_text().splitlines()
    print(part1(lines))


def jokers_high_type(hand):
    without_jokers = Counter(hand.cards.replace('J', ''))
    if not without_jokers:
        # nice
        return HandType.FIVE_OF_A_KIND
    [(most_common, _)] = without_jokers.most_common(1)
    new_cards = hand.cards.replace('J', most_common)
    return Hand.from_cards(new_cards).type


@pytest.mark.parametrize("cards,high_type", [
    ('32T3K', HandType.ONE_PAIR),
    ('KK677', HandType.TWO_PAIR),
    ('T55J5', HandType.FOUR_OF_A_KIND),
    ('KTJJT', HandType.FOUR_OF_A_KIND),
    ('QQQJA', HandType.FOUR_OF_A_KIND)
])
def test_jokers_high_type(cards, high_type):
    hand = Hand.from_cards(cards)
    assert jokers_high_type(hand) == high_type


def jokerfy_hands(hands):
    return [
        replace(
            hand,
            type=jokers_high_type(hand),
            ranks=JOKER_CARD_RANKS,
        ) for hand in hands
    ]


def part2(lines):
    return winnings(lines, jokerfy_hands)


def test_part2():
    assert part2(EXAMPLE) == 5905


if __name__ == '__main__':
    print(part2(lines))
