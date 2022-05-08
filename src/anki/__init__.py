from dataclasses import dataclass, field
from enum import Enum
from itertools import count
import sqlite3

__version__ = '0.1.0'



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
    id: int = field(default_factory=count().__next__)


@dataclass
class AnkiDB:
    dbname: str

    def _create_tables(self, con: sqlite3.Connection):
        con.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS decks (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY,
                front TEXT,
                back TEXT,
                times_reviewed INTEGER DEFAULT 0,
                review_score INTEGER DEFAULT 0,
                deck_id INTEGER,
                FOREIGN KEY(deck_id) REFERENCES decks(id)
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
    
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
        new_user = User(name=db_user['name'], id=db_user['id'])
        return new_user

    
    def create_deck(self, name: str) -> Deck:
        con = self.connect()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        sql = f"INSERT INTO decks (name) VALUES ('{name}')"
        cur.execute(sql)
        deck_id = cur.lastrowid
        db_deck = cur.execute(f"SELECT * FROM decks WHERE id = {deck_id}").fetchone()
        con.commit()
        con.close()
        new_deck = Deck(name=db_deck['name'], id=db_deck['id'])
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
        new_card = Card(front=db_card['front'], back=db_card['back'],
                        id=db_card['id'])
        return new_card

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

