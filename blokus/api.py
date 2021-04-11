from flask import Blueprint
from flask_restful import Api

from blocus.resources.game import GameCollection, GameItem
from blocus.resources.block import BlockCollection, BlockItem
from blocus.resources.gamestate import GameStateItem
from blocus.resources.transaction import TransactionItem

api_bp = Blueprint("api", __name__)
api = Api(api_bp)

api.add_resource(GameCollection, "/api/games/")
api.add_resource(GameItem, "/api/games/<game>/")