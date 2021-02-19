from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine
from sqlalchemy import event

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)



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

    game = db.relationship("Game", back_populates="board_state", uselist=False)



class Game(db.Model):
    __tablename__ = 'game'
    id = db.Column(db.Integer, primary_key=True)
    board_state_id = db.Column(db.Integer, db.ForeignKey("state.id"), unique=True)

    players = db.relationship("Player", back_populates="game")
    board_state = db.relationship("State", back_populates="game")




class Player(db.Model):
    __tablename__ = 'player'
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String, nullable=False)
    available_blocks = db.Column(db.String)
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"))
    game = db.relationship("Game", back_populates="players")
