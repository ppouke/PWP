import os
import pytest
import tempfile

import app

from app import State, Game, Player
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture
def db_handle():
    db_fd, db_fname = tempfile.mkstemp()
    app.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.app.config["TESTING"] = True

    with app.app.app_context():
        app.db.create_all()

    yield app.db

    app.db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)



# Define test instances of models
def _get_player(color="red"):
    return Player(
        color="red"
    )


def _get_game():
    return Game()


def _get_state():
    return State(
    placed_blocks ="none"
    )




def test_created_instance(db_handle):

    """
    1.Test creation of instance of each model and save them to them
    database with valid values.

    2. Test the everything is found from the database and all relationships
     are correct.

    3. Test updating exisiting models in the database
    (i.e. player:color, players in game, and state:placed blocks)

    4. Test removing model instances

    Note. No onModify and onDelete used in database as of current
    """

    # 1 . Create all models
    player = _get_player()
    game = _get_game()
    state = _get_state()

    game.players.append(player)
    game.board_state = state

    db_handle.session.add(player)
    db_handle.session.add(game)
    db_handle.session.add(state)
    db_handle.session.commit()

    # 2a. Check all exist
    assert Player.query.count() == 1
    assert Game.query.count() == 1
    assert State.query.count() == 1

    db_player = Player.query.first()
    db_game = Game.query.first()
    db_state = State.query.first()


    #2b. Check relationships on both sides
    assert db_game.board_state == db_state
    assert db_state.game == db_game
    assert db_player.game == db_game
    assert db_player in db_game.players


    #3 Update existing models

    player.color = "orange"
    player2 = _get_player("blue")
    db_handle.session.add(player2)
    game.players.append(player2)
    state.placed_blocks = "placed blocks"
    db_handle.session.commit()


    db_player2 = Player.query.filter_by(id=2).first()
    assert db_player.color == "orange"
    assert db_player2 in db_game.players
    assert db_state.placed_blocks == "placed blocks"

    #4 Remove existing models

    db_handle.session.delete(state)
    db_handle.session.delete(game)
    db_handle.session.delete(player)
    db_handle.session.delete(player2)

    db_handle.session.commit()

    assert Player.query.count() == 0
    assert Game.query.count() == 0
    assert State.query.count() == 0

def test_state_game_one_to_one(db_handle):

    """
    Test that the relationship between game and state is one to one
    i.e. we can't assign the same board state to two games
    """

    state = _get_state()
    game1 = _get_game()
    game2 = _get_game()

    game1.board_state = state
    game2.board_state = state

    db_handle.session.add(state)
    db_handle.session.add(game1)
    db_handle.session.add(game2)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

def test_mandatory_columns(db_handle):
    """
    Test mandatory columns for player and state.
    """
    #Player
    player = _get_player()
    player.color = None
    db_handle.session.add(player)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()

    #State

    state = _get_state()
    state.placed_blocks = None
    db_handle.session.add(state)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
