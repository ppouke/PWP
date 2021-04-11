from flask import Blueprint
from flask_restful import Api

from blokus.resources.game import GameCollection, GameItem
from blokus.resources.block import BlockCollection, BlockItem
from blokus.resources.gamestate import GameStateItem
from blokus.resources.transaction import TransactionFactory, TransactionItem
from blokus.resources.player import Player

api_bp = Blueprint("api", __name__)
api = Api(api_bp)

api.add_resource(GameCollection, "/api/games/")
api.add_resource(GameItem, "/api/games/<game>/")
api.add_resource(BlockCollection, "/api/blocks/")
api.add_resource(BlockItem, "/api/blocks/<block>/")
api.add_resource(TransactionFactory, "/api/transactions/")
api.add_resource(TransactionItem, "/api/transactions/<transaction>/")
api.add_resource(PlayerItem, "/api/games/<game>/players/<player>/")
