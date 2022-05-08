from anki import __version__, Card, TextBox, Deck, Grade, User, Session
from pytest import fixture

@fixture
def front():
    return TextBox(text="Hello")

@fixture
def back():
    return TextBox(text="World")

@fixture
def card(front, back):
    return Card(
        front=front,
        back=back
        )

@fixture
def deck(card):
    return Deck(name="My Study Deck", cards=[card])

@fixture
def user():
    return User(name="John")

@fixture
def session(user):
    return Session(user=user)


def test_version():
    assert __version__ == '0.1.0'

def test_create_card(front, card):
    assert isinstance(card, Card)
    assert isinstance(front, TextBox)
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
    assert user.id == session.id
    u2 = User(name="Jane").id == 1
    assert Session(user=u2).id == 1
    assert Session(user=u2).id == 2

def test_connect_to_db():
    """Test that we can connect to the database"""
    ...