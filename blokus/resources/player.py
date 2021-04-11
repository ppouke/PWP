import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from blokus import db
from blokus.models import *
from blokus.constants import *
from blokus.utils import BlokusBuilder, create_error_response

class PlayerItem(Resource):
    def get(self, color):
        db_player = Player.query.filter_by(color = color).first()
        if db_player is None:
             return create_error_response(
                404, "Not found",
                "No player was found with the color id {}".format(color)
            )

        body = BlokusBuilder(
            color = db_player.color,
            used_blocks = db_player.used_blocks
        )

        db_game= Game.query.filter_by(id = db_player.game_id)

        body.add_namespace("blokus", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.player", game = db_game.handle , player = db_player.color))
        body.add_contol("profile", PLAYER_PROFILE)
        body.add_control("game", url_for("api.game", game = db_game.handle))

        return Response(json.dumps(body), 200, mimetype = MASON)
