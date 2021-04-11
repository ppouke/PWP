import click
from flask.cli import with_appcontext
from blokus import db

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

class Game(db.Model):
    __tablename__ = 'game'
    id = db.Column(db.Integer, primary_key=True)
    handle = db.Column(db.String, nullable=False)

    placed_blocks = db.Column(db.String, nullable=False)
    turn_information = db.Column(db.Integer, db.ForeignKey("player.id"))

    players = db.relationship("Player", back_populates="game")

    current_transaction = db.relationship("Transaction", back_populates="game")

    @staticmethod
    def get_schema():
        schema = {
            "type" = "object",
            "required": ["handle"]
        }
        props = schema["properties"] = {}
        props["handle"] = {
            "description": "Games unique handle",
            "type". "string"
        }
        props["placed_blocks"] = {
            "description": "Games board state as string",
            "type". "string"
        }
        return schema





class Player(db.Model):
    __tablename__ = 'player'
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.Integer, nullable=False)
    used_blocks = db.Column(db.String)
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"))
    game = db.relationship("Game", back_populates="players", ondelete="CASCADE")

    @staticmethod
    def get_schema():
        schema = {
            "type" = "object",
            "required": ["color"]
        }
        props = schema["properties"] = {}
        props["color"] = {
            "description": "Players color id (1-4)",
            "type". "integer"
        }
        props["used_blocks"] = {
            "description": "Players used blocks comma separated list",
            "type". "string"
        }
        return schema

    

class Block(db.Model):
    __tablename__ = 'block'
    id = db.Column(db.Integer, primary_key=True)
    shape = db.Column(db.String, nullable=False)

class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    player = db.relationship("Player")
    game = db.relationship("Game", ondelete="CASCADE")
    commit = db.Column(db.Integer)

    used_blocks = db.Column(db.String)
    board_state = db.Column(db.String)

    @staticmethod
    def get_schema():
        schema = {
            "type" = "object",
            "required": ["player", "game"]
        }
        props = schema["properties"] = {}
        props["player"] = {
            "description": "Player id whose block we want to place",
            "type". "integer"
        }
        props["game"] = {
            "description": "Handle for the game that we want to change the state of",
            "type": "string"
        }
        props["used_blocks"] = {
            "description": "Blocks used by the player",
            "type": "string"
        }
        props["board_state"] = {
            "description": "Blocks placed on the board",
            "type": "string"
        }
        props["commit"] = {
            "description": "Set 1 if you want to commit the transaction",
            "type": "integer"
        }
        return schema

@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()

