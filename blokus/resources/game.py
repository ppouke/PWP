import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from blokus import db
from blokus.models import *
from blokus.constants import *
from blokus.utils import BlokusBuilder, create_error_response

class GameItem(Resource):

    def get(self, game):
        db_game = Sensor.query.filter_by(handle=game).first()
        if db_game is None:
            return create_error_response(404, "Not found", 
                "No game was found with the name {}".format(game)
            )
        
        body = BlokusBuilder(
                handle=db_game.handle,
                players=db_game.players,
                board_state=db_game.board_state
            )
        body.add_namespace("blokus", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.GameItem", handle=game))
        body.add_control("profile", GAME_PROFILE)
        body.add_control("collection", url_for("api.GameCollection"))
        body.add_control_delete_game(db_game)
        body.add_control_add_player(db_game)
        body.add_control_get_games()

        return Response(json.dumps(body), 200, mimetype=MASON)

    def delete(self, game):
        db_game = Game.query.filter_by(handle=game).first()
        if db_game is None:
            return create_error_response(404, "Not found", 
                "No game was found with the name {}".format(game)
            )

        db.session.delete(db_game)
        db.session.commit()

        return Response(status=204)

class GameCollection(Resource):

    def get(self):
        body = BlokusBuilder()

        body.add_namespace("blokus", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.GameCollection"))
        body.add_control_get_blocks()
        body.add_control_get_transactions()
        body.add_control_add_game()
        body["items"] = []
        for game in Game.query.all():
            item = BlokusBuilder(
                handle=game.handle,
                players=game.players,
                board_state=game.board_state
            )
            item.add_control("self", url_for("api.GameItem", game=game.handle))
            item.add_control("profile", GAME_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self):
        if not request.json:
            return create_error_response(415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Game.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        game = Game(
            handle=request.json["handle"]
        )

        try:
            db.session.add(game)
            db.session.commit()
        except IntegrityError:
            return create_error_response(409, "Already exists", 
                "Game with name '{}' already exists.".format(request.json["handle"])
            )

        return Response(status=201, headers={
            "Location": url_for("api.GameItem", game=request.json["handle"])
        })
