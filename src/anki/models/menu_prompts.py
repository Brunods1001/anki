
from enum import Enum


class Grade(Enum):
    EASY = 1
    MEDIUM = 0
    HARD = -1
    FAIL = -2

class MenuPrompt(Enum):
    CREATE_USER = 1
    LOGIN = 2
    EXIT = 3


class LoggedInMenuPrompt(Enum):
    CREATE_DECK = 1
    CHOOSE_DECK = 2
    LOGOUT = 3


class UserPrompt(Enum):
    UPDATE_USER = 1
    DELETE_USER = 2


class DeckPrompt(Enum):
    CREATE_CARD = 1
    CHOOSE_CARD = 2
    REVIEW_DECK = 3
    EXIT_DECK = 4


class CardPrompt(Enum):
    UPDATE_CARD = 1
    DELETE_CARD = 2
    EXIT_CARD = 3


def print_options(Options: Enum) -> Enum:
    print("Choose an option:")
    for option in Options:
        print(f"{option.value}: {option.name}")
    return Options(int(input("Enter your choice: ")))