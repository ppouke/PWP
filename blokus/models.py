import click
from flask.cli import with_appcontext
from blokus import db

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    handle = db.Column(db.String, nullable=False)

    placed_blocks = db.Column(db.String, nullable=False)
    turn_information = db.relationship("Player")

    players = db.relationship("Player", back_populates="game", cascade="all, delete")

    @staticmethod
    def get_schema():
        schema = {
            "type" : "object",
            "required": ["handle"]
        }
        props = schema["properties"] = {}
        props["handle"] = {
            "description": "Games unique handle",
            "type": "string"
        }
        props["placed_blocks"] = {
            "description": "Games board state as string",
            "type": "string"
        }
        return schema





class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.Integer, nullable=False)
    used_blocks = db.Column(db.String)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id', ondelete="CASCADE"))
    game = db.relationship("Game", back_populates="players")

    @staticmethod
    def get_schema():
        schema = {
            "type" : "object",
            "required": ["color"]
        }
        props = schema["properties"] = {}
        props["color"] = {
            "description": "Players color id (1-4)",
            "type": "integer"
        }
        props["used_blocks"] = {
            "description": "Players used blocks comma separated list",
            "type": "string"
        }
        return schema



class Block(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shape = db.Column(db.String, nullable=False)

    @staticmethod
    def get_schema():
        schema = {
            "type" : "object",
            "required": ["shape"]
        }
        props = schema["properties"] = {}
        props["shape"] = {
            "description": "5*5 long string describing the shape of the block. 0 for free and 1 for reserved slot",
            "type": "string"
        }

        return schema

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player.id', ondelete="CASCADE"))
    player = db.relationship("Player", foreign_keys = 'player_id')
    game = db.relationship("Game", foreign_keys = ' game_id')
    commit = db.Column(db.Integer)

    used_blocks = db.Column(db.String)
    board_state = db.Column(db.String)
    next_player = db.Column(db.Integer)

    @staticmethod
    def get_schema():
        schema = {
            "type" : "object",
            "required": ["player", "game"]
        }
        props = schema["properties"] = {}
        props["player"] = {
            "description": "Player id whose block we want to place",
            "type": "integer"
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
        props["next_player"] = {
            "description": "Color id of the next player",
            "type": "integer"
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

@click.command("testgen")
@with_appcontext
def generate_test_data():
    game = Game()
    player_1 = Player()
    player_2 = Player()

    game.players.append(player_1)
    game.players.append(player_2)
    game.placed_blocks = "0"*400
    game.turn_information = player_1

    player_1.color = 1
    player_1.used_blocks = "1,2"
    player_2.color = 2
    player_2.used_blocks = "1"

    block_1 = Block()
    block_1.shape = ("00000"
                     "00000"
                     "00100"
                     "00000"
                     "00000")
    block_2 = Block()
    block_2.shape = ("00100"
                     "00100"
                     "00100"
                     "00100"
                     "00100")

    trans = Transaction()
    trans.game = game
    trans.player = player_1
    trans.used_blocks = "1,2"
    trans.board_state = "0"*400

    db.session.add(game)
    db.session.add(trans)
    db.session.add(block_1)
    db.session.add(block_2)
