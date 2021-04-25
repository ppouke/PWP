from flask import Blueprint
from flask_restful import Api

from blokus.resources.game import GameCollection, GameItem
from blokus.resources.block import BlockCollection, BlockItem
from blokus.resources.transaction import TransactionFactory, TransactionItem
from blokus.resources.player import PlayerItem

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

api.add_resource(GameCollection, "/games/")
api.add_resource(GameItem, "/games/<game>/")
api.add_resource(BlockCollection, "/blocks/")
api.add_resource(BlockItem, "/blocks/<block>/")
api.add_resource(TransactionFactory, "/transactions/")
api.add_resource(TransactionItem, "/transactions/<transaction>/")
api.add_resource(PlayerItem, "/games/<game>/players/<player>/")


