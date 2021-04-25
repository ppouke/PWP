import click
from flask.cli import with_appcontext
from blokus import db

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    handle = db.Column(db.String, nullable=False, unique=True)

    placed_blocks = db.Column(db.String)
    turn_information = db.relationship("Player", uselist=False)

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
            "type": "string",
            "minLength": 400,
            "maxLength": 400,
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
            "type": "integer",
            "minimum": 1,
            "maximum": 4
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
            "type": "string",
            "minLength": 25,
            "maxLength": 25,
        }

        return schema

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player.id', ondelete="CASCADE"))
    player = db.relationship("Player", foreign_keys = [player_id])
    game = db.relationship("Game", foreign_keys = [game_id])
    commit = db.Column(db.Integer)

    used_blocks = db.Column(db.String)
    board_state = db.Column(db.String)
    next_player = db.Column(db.Integer, db.ForeignKey('player.id'))

    @staticmethod
    def get_schema():
        schema = {
            "type" : "object",
            "required": ["player", "game"]
        }
        props = schema["properties"] = {}
        props["player"] = {
            "description": "Player id whose block we want to place",
            "type": "integer",
            "minimum": 1,
            "maximum": 4
        }
        props["game"] = {
            "description": "Handle for the game that we want to change the state of",
            "type": "string"
        }
        props["used_blocks"] = {
            "description": "Blocks used by the player",
            "type": "string"
        }
        props["placed_blocks"] = {
            "description": "Blocks placed on the board",
            "type": "string",
        }
        props["next_player"] = {
            "description": "Color id of the next player",
            "type": "integer",
        }
        props["commit"] = {
            "description": "Set 1 if you want to commit the transaction",
            "type": "integer"
        }
        return schema

@click.command("init-db")
@with_appcontext
def init_db_command():
    """
    This function initializes the database
    """
    db.create_all()
    generate_blocks()


def generate_blocks():
    """
    This function populates the database with valid blocks
    """
    blocks = []

    blocks.append(Block())
    blocks[0].shape = ("00000"
                       "00000"
                       "00100"
                       "00000"
                       "00000")
    blocks.append(Block())
    blocks[1].shape = ("00000"
                       "00100"
                       "00100"
                       "00000"
                       "00000")
    blocks.append(Block())
    blocks[2].shape = ("00000"
                       "00100"
                       "00100"
                       "00100"
                       "00000")
    blocks.append(Block())
    blocks[3].shape = ("00100"
                       "00100"
                       "00100"
                       "00100"
                       "00000")
    blocks.append(Block())
    blocks[4].shape = ("00100"
                       "00100"
                       "00100"
                       "00100"
                       "00100")
    blocks.append(Block())
    blocks[5].shape = ("00000"
                       "00100"
                       "01110"
                       "00000"
                       "00000")
    blocks.append(Block())
    blocks[6].shape = ("00000"
                       "00000"
                       "01110"
                       "01010"
                       "00000")
    blocks.append(Block())
    blocks[7].shape = ("00000"
                       "00110"
                       "00100"
                       "00100"
                       "00000")
    blocks.append(Block())
    blocks[8].shape = ("00000"
                       "01100"
                       "00100"
                       "00100"
                       "00000")
    blocks.append(Block())
    blocks[9].shape = ("00000"
                       "00110"
                       "00100"
                       "01100"
                       "00000")
    blocks.append(Block())
    blocks[10].shape = ("00000"
                        "01100"
                        "00100"
                        "00110"
                        "00000")
    blocks.append(Block())
    blocks[11].shape = ("00010"
                        "00110"
                        "00100"
                        "00100"
                        "00000")

    for b in blocks:
        db.session.add(b)
    db.session.commit()
