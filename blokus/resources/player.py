import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from blokus import db
from blokus.models import *
from blokus.constants import *
from blokus.utils import BlokusBuilder, create_error_response

class PlayerItem(Resource):
    def get(self, game, player):
        """
        This function answers to the get-request for the player-resource at /api/game/<game>/players/<player>/
        """
        db_game = Game.query.filter_by(handle=game).first()
        if db_game is None:
             return create_error_response(
                404, "Not found",
                "No game was found with the handle {}".format(game)
            )
        db_player = Player.query.filter_by(color=player, game_id=db_game.id).first()
        if db_player is None:
             return create_error_response(
                404, "Not found",
                "No player was found with the color id {}".format(player)
            )

        body = BlokusBuilder(
            color = db_player.color,
            used_blocks = db_player.used_blocks
        )

        db_game= db_player.game

        body.add_namespace("blokus", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.playeritem", game = db_game.handle , player = str(db_player.color)))
        body.add_control("profile", PLAYER_PROFILE)
        body.add_control("game", url_for("api.gameitem", game = db_game.handle))

        return Response(json.dumps(body), 200, mimetype = MASON)
