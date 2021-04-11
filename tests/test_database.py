import os
import pytest
import tempfile
from datetime import datetime
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

from blokus import create_app, db
from blokus.models import Game, Player, Transaction, Block
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture
def app():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }

    app = create_app(config)

    with app.app_context():
        db.create_all()

    yield app

    os.close(db_fd)
    os.unlink(db_fname)



# Define test instances of models
def _get_player(color=1):
    return Player(
        color=1,
        used_blocks=""
    )


def _get_game():
    return Game(handle="best game", placed_blocks="0"*400)

def _get_block():
    return Block(shape=("00000"
                        "00000"
                        "00100"
                        "00000"
                        "00000")
    )

def _get_transaction():
    return Transaction()






def test_created_instance(app):

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
    with app.app_context():
        # 1 . Create all models
        player = _get_player()
        game = _get_game()
        block = _get_block()
        trans = _get_transaction()

        trans.game = game
        trans.player = player

        game.players.append(player)

        db.session.add(player)
        db.session.add(game)
        db.session.add(block)
        db.session.add(trans)
        db.session.commit()

        # 2a. Check all exist
        assert Player.query.count() == 1
        assert Game.query.count() == 1
        assert Transaction.query.count() == 1

        db_player = Player.query.first()
        db_game = Game.query.first()
        db_trans = Transaction.query.first()
        db_block = Block.query.first()


        #2b. Check relationships on both sides
        assert db_player.game == db_game
        assert db_player in db_game.players
        assert db_player == db_trans.player
        assert db_game == db_trans.game

        #3 Update existing models

        player.color = 2
        player2 = _get_player(3)
        db.session.add(player2)
        game.players.append(player2)
        game.placed_blocks = "1234"
        block.shape = "0000"
        db.session.commit()


        db_player2 = Player.query.filter_by(id=2).first()
        assert db_player.color == 2
        assert db_player2 in db_game.players
        assert db_game.placed_blocks == "1234"
        assert db_block.shape == "0000"

        #4 Remove existing models

        db.session.delete(game)
        db.session.delete(player)
        db.session.delete(player2)
        db.session.delete(trans)
        db.session.delete(block)

        db_handle.session.commit()

        assert Player.query.count() == 0
        assert Game.query.count() == 0
        assert Transaction.query.count() == 0
        assert Block.query.count() == 0

def test_player_ondelete_game(app):
    """
    Tests if players get deleted when the game is deleted
    """

    with app.app_context():
        player = _get_player()
        game = _get_game()

        game.players.append(player)

        db.session.add(game)
        db.session.commit()
        db.session.delete(game)
        db.session.commit()
        assert player is None


def test_mandatory_columns(app):
    """
    Test mandatory columns for player and state.
    """

    with app.app_context():
        #Player
        player = _get_player()
        player.color = None
        db.session.add(player)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()
