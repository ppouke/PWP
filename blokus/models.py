import click
from flask.cli import with_appcontext
from blocus import db

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

class State(db.Model):
    __tablename__ = 'state'
    id = db.Column(db.Integer, primary_key=True)
    placed_blocks = db.Column(db.String, nullable=False)
    turn_information = db.Column(db.Integer, db.ForeignKey("player.id"))

    game = db.relationship("Game", back_populates="board_state", uselist=False, ondelete="CASCADE")



class Game(db.Model):
    __tablename__ = 'game'
    id = db.Column(db.Integer, primary_key=True)
    handle = db.Column(db.String, nullable=False)
    board_state_id = db.Column(db.Integer, db.ForeignKey("state.id"), unique=True)

    players = db.relationship("Player", back_populates="game")
    board_state = db.relationship("State", back_populates="game")




class Player(db.Model):
    __tablename__ = 'player'
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.Integer, nullable=False)
    used_blocks = db.Column(db.String)
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"))
    game = db.relationship("Game", back_populates="players", ondelete="CASCADE")
    

class Block(db.Model):
    __tablename__ = 'block'
    id = db.Column(db.Integer, primary_key=True)
    shape = db.Column(db.String, nullable=False)

class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    player = db.relationship("Player")
    board_state = db.relationship("State")

    used_blocks = db.Column(db.String)
    board_state = db.Column(db.String)

@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()

