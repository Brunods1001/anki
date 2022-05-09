from dataclasses import dataclass, field
from enum import Enum
from itertools import count
import sqlite3
import sys

__version__ = "0.1.0"


# Create module containing Cards


class Grade(Enum):
    EASY = 1
    MEDIUM = 0
    HARD = -1
    FAIL = -2


@dataclass(order=True)
class Card:
    front: str = field(compare=False)
    back: str = field(compare=False)
    id: int = field(default_factory=count().__next__)
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
    id: int = field(default_factory=count().__next__)


@dataclass
class User:
    name: str
    decks: list[Deck] = field(default_factory=list)
    id: int = field(default_factory=count().__next__)


@dataclass
class AnkiDB:
    dbname: str

    def __post_init__(self):
        self.setup_new_db()

    def _create_tables(self, con: sqlite3.Connection):
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS decks (
                id INTEGER PRIMARY KEY,
                name TEXT,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY,
                front TEXT,
                back TEXT,
                times_reviewed INTEGER DEFAULT 0,
                review_score INTEGER DEFAULT 0,
                deck_id INTEGER,
                FOREIGN KEY(deck_id) REFERENCES decks(id)
            )
        """
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """
        )

    def setup_new_db(self):
        con = self.connect()
        self._create_tables(con=con)
        con.close()

    def connect(self) -> sqlite3.Connection:
        """Creates a new connection to the database and yields it."""
        con = sqlite3.connect(self.dbname)
        return con

    def execute_and_commit(self, sql: str):
        con = self.connect()
        cur = con.cursor()
        cur.execute(sql)
        con.commit()
        con.close()

    def create_user(self, name: str) -> User:
        con = self.connect()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        sql = f"INSERT INTO users (name) VALUES ('{name}')"
        cur.execute(sql)
        user_id = cur.lastrowid
        db_user = cur.execute(f"SELECT * FROM users WHERE id = {user_id}").fetchone()
        con.commit()
        con.close()
        new_user = User(name=db_user["name"], id=db_user["id"])
        return new_user

    def create_deck(self, name: str, user_id: int) -> Deck:
        con = self.connect()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        sql = f"INSERT INTO decks (name, user_id) VALUES ('{name}', {user_id})"
        cur.execute(sql)
        deck_id = cur.lastrowid
        db_deck = cur.execute(f"SELECT * FROM decks WHERE id = {deck_id}").fetchone()
        con.commit()
        con.close()
        new_deck = Deck(name=db_deck["name"], id=db_deck["id"])
        return new_deck

    def create_card(self, front: str, back: str, deck_id: int) -> Card:
        con = self.connect()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        sql = f"INSERT INTO cards (front, back, deck_id) VALUES ('{front}', '{back}', {deck_id})"
        cur.execute(sql)
        card_id = cur.lastrowid
        db_card = cur.execute(f"SELECT * FROM cards WHERE id = {card_id}").fetchone()
        con.commit()
        con.close()
        new_card = Card(front=db_card["front"], back=db_card["back"], id=db_card["id"])
        return new_card

    def update_card(
        self, card_id: int, front: str | None = None, back: str | None = None,
        review_score: int | None = None, times_reviewed: int | None = None,
    ):
        print(f"Updating card {card_id}")
        con = self.connect()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        if front is not None:
            sql = f"UPDATE cards SET front = '{front}' WHERE id = {card_id}"
            cur.execute(sql)
        if back is not None:
            sql = f"UPDATE cards SET back = '{back}' WHERE id = {card_id}"
            cur.execute(sql)
        if review_score is not None:
            print("Changing review score")
            print(review_score)
            sql = f"UPDATE cards SET review_score = {review_score} WHERE id = {card_id}"
            cur.execute(sql)
        if times_reviewed is not None:
            sql = f"UPDATE cards SET times_reviewed = {times_reviewed} WHERE id = {card_id}"
            cur.execute(sql)

        con.commit()
        con.close()
    
    def delete_card(self, card_id: int):
        con = self.connect()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        sql = f"DELETE FROM cards WHERE id = {card_id}"
        cur.execute(sql)
        con.commit()
        con.close()


@dataclass
class Session:
    """
    A session is the interaction between the user and the cards in a deck.
    It handles database connections and queries.
    """

    user: User
    db: AnkiDB
    id: int = field(default_factory=count().__next__)

    def run(self):
        # connect to db
        con = self.db.connect()
        # get all decks

        # prompt user to choose deck
        # disconnect from db (automatically)


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


@dataclass
class App:
    db: AnkiDB
    decks: dict[int, Deck] = field(default_factory=dict)
    user: User | None = None

    def create_user(self):
        username = input("Enter your username: ")
        self.user = self.db.create_user(name=username)

    def login(self):
        """Takes a username and password and logs the user in."""
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        con = self.db.connect()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        sql = f"SELECT * FROM users WHERE name = '{username}'"
        db_user = cur.execute(sql).fetchone()
        if db_user is None:
            print("User not found.")
        else:
            self.user = User(name=db_user["name"], id=db_user["id"])
        con.close()

    def load_decks(self):
        """Loads all decks for the logged in user."""
        print("Loading decks")
        self.decks = {}
        if self.user is None:
            print("You must be logged in to load decks.")
        else:
            con = self.db.connect()
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            sql = f"SELECT * FROM decks WHERE user_id = {self.user.id}"
            decks = cur.execute(sql).fetchall()
            # TODO: only load cards when needed
            for deck in decks:
                cards_row = cur.execute(
                    f"SELECT * FROM cards WHERE deck_id = {deck['id']} ORDER BY review_score, times_reviewed"
                ).fetchall()
                cards = [
                    Card(
                        front=i["front"],
                        back=i["back"],
                        id=i["id"],
                        _Card__review_score=i["review_score"],
                        _Card__times_reviewed=i["times_reviewed"],
                    )
                    for i in cards_row
                ]
                self.decks[deck["id"]] = Deck(
                    name=deck["name"], id=deck["id"], cards=cards
                )
            con.close()

    def create_deck(self):
        """Creates a new deck."""
        deck_name = input("Enter the name of the deck: ")
        deck = self.db.create_deck(name=deck_name, user_id=self.user.id)
        self.decks[deck.id] = deck

    def create_card(self, deck_id: int):
        """Creates a new card."""
        front = input("Enter the front of the card: ")
        back = input("Enter the back of the card: ")
        self.db.create_card(front=front, back=back, deck_id=deck_id)

    def logout(self):
        """Logs the user out."""
        self.user = None

    def update_card(self, card: Card):
        is_updating = True
        while is_updating:
            print(f"Updating card: {card}")
            print("1: Update front")
            print("2: Update back")
            print("3: Update both")
            print("4: Return to main menu")
            choice = int(input("Enter your choice: "))
            if choice == 1:
                front = input("Enter the new front: ")
                self.db.update_card(card_id=card.id, front=front)
                is_updating = False
            elif choice == 2:
                back = input("Enter the new back: ")
                self.db.update_card(card_id=card.id, back=back)
                is_updating = False
            elif choice == 3:
                front = input("Enter the new front: ")
                back = input("Enter the new back: ")
                self.db.update_card(card_id=card.id, front=front, back=back)
                is_updating = False
            elif choice == 4:
                is_updating = False
            else:
                print("Invalid choice.")

    def delete_card(self, card: Card):
        """Deletes a card from the database."""
        self.db.delete_card(card_id=card.id)
    
    def review_deck(self, deck: Deck):
        """Reviews the cards in a deck"""
        for card in deck.cards:
            print(f"Reviewing card: {card}")
            print(f"Front of card: {card.front}")
            input("Review card. Press enter to continue.")
            print(f"Back of card: {card.back}")
            grade = print_options(Grade)
            print(card.review_score)
            card.review(grade=grade)
            print(card.review_score)
            self.db.update_card(card_id=card.id, review_score=card.review_score, times_reviewed=card.times_reviewed)



    def run(self):
        """Runs the app until the user exits"""
        is_running = True
        while is_running:
            if self.user is None:
                menu_choice: MenuPrompt = print_options(MenuPrompt)
                match menu_choice:
                    case MenuPrompt.CREATE_USER:
                        self.create_user()
                    case MenuPrompt.LOGIN:
                        self.login()
                    case MenuPrompt.EXIT:
                        is_running = False
                    case _:
                        print("Invalid choice.")
            elif self.user is not None:
                print("Logged in as", self.user.name)
                logged_in_menu_choice: LoggedInMenuPrompt = print_options(
                    LoggedInMenuPrompt
                )
                match logged_in_menu_choice:
                    case LoggedInMenuPrompt.CREATE_DECK:
                        self.create_deck()
                    case LoggedInMenuPrompt.CHOOSE_DECK:
                        # list all decks belonging to the current user
                        print("Choose a deck:")
                        self.load_decks()
                        if len(self.decks) == 0:
                            print("You have no decks.")
                            continue
                        for deck_id, deck in self.decks.items():
                            print(deck_id, deck)
                        # prompt user to choose deck
                        deck_id = int(input("Enter your choice: "))
                        in_deck_menu = True
                        while in_deck_menu:
                            chosen_deck: Deck = self.decks[deck_id]
                            chosen_cards = chosen_deck.cards
                            print(f"Chosen deck: {chosen_deck}")
                            deck_prompt_choice: DeckPrompt = print_options(DeckPrompt)
                            match deck_prompt_choice:
                                case DeckPrompt.CREATE_CARD:
                                    self.create_card(deck_id=deck_id)
                                    self.load_decks()
                                case DeckPrompt.CHOOSE_CARD:
                                    # list available cards in deck
                                    print("Choose a card:")
                                    for i, card in enumerate(chosen_cards):
                                        print(i, card)
                                    # prompt user to choose card
                                    card_idx = int(input("Enter your choice: "))
                                    chosen_card: Card = chosen_cards[card_idx]
                                    print(f"Chosen card: {chosen_card}")
                                    card_prompt_choice: CardPrompt = print_options(
                                        CardPrompt
                                    )
                                    match card_prompt_choice:
                                        case CardPrompt.UPDATE_CARD:
                                            self.update_card(chosen_card)
                                            self.load_decks()
                                        case CardPrompt.DELETE_CARD:
                                            self.delete_card(chosen_card)
                                            self.load_decks()
                                        case CardPrompt.EXIT_CARD:
                                            pass
                                        case _:
                                            print("Invalid choice.")
                                case DeckPrompt.REVIEW_DECK:
                                    self.review_deck(deck=chosen_deck)
                                    self.load_decks()
                                case DeckPrompt.EXIT_DECK:
                                    in_deck_menu = False
                                case _:
                                    print("Invalid choice.")
                    case LoggedInMenuPrompt.LOGOUT:
                        self.logout()
                    case _:
                        print("Invalid choice.")

