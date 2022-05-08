from dataclasses import dataclass, field
from enum import Enum
from itertools import count

__version__ = '0.1.0'


# Create module containing Cards and TextBoxes
@dataclass
class TextBox:
    text: str = ""


class Grade(Enum):
    EASY = 1
    MEDIUM = 0
    HARD = -1
    FAIL = -2


@dataclass(order=True)
class Card:
    front: TextBox = field(compare=False)
    back: TextBox = field(compare=False)
    __times_reviewed: int = field(default=0)
    __review_score: int = field(default=0)

    @property
    def times_reviewed(self):
        return self.__times_reviewed
    
    @property
    def review_score(self):
        return self.__review_score

    def review(self, grade: Grade):
        self.__times_reviewed += 1
        match grade:
            case Grade.EASY:
                self.__review_score += 1
            case Grade.MEDIUM:
                self.__review_score += 0
            case Grade.HARD:
                self.__review_score -= 1
            case Grade.FAIL:
                self.__review_score -= 2


@dataclass
class Deck:
    name: str
    cards: list[Card] = field(default_factory=list)

@dataclass
class User:
    name: str
    id: int = field(default_factory=count().__next__)


@dataclass
class Session:
    """
    A session is the interaction between the user and the cards in a deck.
    It handles database connections and queries.
    """
    user: User
    id: int = field(default_factory=count().__next__)


# Begin a session
# connect to the database (or csv?)

# get a list of all decks

# choose a deck

# review cards in the deck in order of increasing review_score

# for each card in the deck, read the front, then read the back, then give yourself a grade

# continue the session with enter, end with the character e.

# print summary stats for the session