import sqlite3
from anki import __version__, Card,  Deck, Grade, User, Session, AnkiDB
from pytest import fixture
EXPECTED_TABLES = {"users", "decks", "cards", "sessions"}

@fixture
def front():
    return "Hello"

@fixture
def back():
    return "World"

@fixture
def card(front, back):
    return Card(
        front=front,
        back=back
        )

@fixture
def deck(card):
    cards = [
        card,
        Card(front="", back=""),
        Card(front="", back=""),
        Card(front="", back=""),
    ]
    return Deck(name="My Study Deck", cards=cards)

@fixture
def user():
    return User(name="John")


@fixture
def ankidb() -> AnkiDB:
    ankidb = AnkiDB(dbname="test_db.sqlite")
    ankidb.setup_new_db()
    yield ankidb

@fixture
def session(ankidb):
    return Session(user=user, db=ankidb)

def test_version():
    assert __version__ == '0.1.0'

def test_create_card(front, card):
    assert isinstance(card, Card)
    assert card.front is front

def test_review_card(card):
    assert card.times_reviewed == 0
    assert card.review_score == 0
    card.review(grade=Grade.FAIL)
    assert card.times_reviewed == 1
    assert card.review_score == -2
    card.review(grade=Grade.EASY)
    card.review(grade=Grade.EASY)
    card.review(grade=Grade.MEDIUM)
    card.review(grade=Grade.EASY)
    assert card.review_score == 1
    card.review(grade=Grade.HARD)
    assert card.review_score == 0

def test_create_deck(deck):
    assert isinstance(deck, Deck)

def test_create_user(user):
    assert user.id == 0
    assert user.name == 'John'
    assert User(name="Jane").id == 1
    assert User(name="John").id == 2

def test_no_interference_between_session_and_user_ids(user, session):
    u2 = User(name="Jane").id == 1
    assert Session(user=u2, db=session.db).id == 1
    assert Session(user=u2, db=session.db).id == 2



def test_connect_to_db(ankidb):
    """Test that we can connect to the database"""
    ankidb.connect().cursor()

def test_tables_are_there(ankidb):
    """Test that tables are created"""
    con = ankidb.connect()
    expected_tables = EXPECTED_TABLES
    res = con.cursor().execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [i[0] for i in res]
    assert set(tables) == expected_tables


def test_create_user_in_db(ankidb):
    user = ankidb.create_user(name="John")
    assert isinstance(user, User)
    con = ankidb.connect()
    con.row_factory = sqlite3.Row
    res = con.cursor().execute(f"SELECT * FROM users WHERE id={user.id}").fetchone()
    assert res['name'] == 'John'

def test_create_user_autoincrements_id(ankidb):
    user1 = ankidb.create_user(name="John1")
    user2 = ankidb.create_user(name="John2")
    assert user1.id == user2.id - 1


def test_create_deck_and_assign_to_user(ankidb):
    user = ankidb.create_user(name="John")
    deck = ankidb.create_deck(name="My Study Deck", user_id=user.id)
    assert isinstance(deck, Deck)
    con = ankidb.connect()
    con.row_factory = sqlite3.Row
    res = con.cursor().execute(f"SELECT * FROM decks WHERE id={deck.id}").fetchone()
    assert res['name'] == 'My Study Deck'

def test_create_card(ankidb):
    user = ankidb.create_user(name="John")
    deck = ankidb.create_deck(name="My Study Deck", user_id=user.id)
    card = ankidb.create_card(front="Hello", back="World", deck_id=deck.id)
    assert isinstance(card, Card)
    con = ankidb.connect()
    con.row_factory = sqlite3.Row
    res = con.cursor().execute(f"SELECT * FROM cards WHERE id={card.id}").fetchone()
    assert res['front'] == 'Hello'
    assert res['back'] == 'World'
    assert res['review_score'] == 0
    
def test_initiate_app():
    """Initiates the app and prompts the user"""
    ...

def test_session(user, session, deck):
    # begin session
    # get the pks of all decks
    # let user choose a deck
    # iterate over all cards in deck in order of increasing review_score
    # for each card, ask the user to read the front, back, and review it
    # once the session ends, print stats
    ...