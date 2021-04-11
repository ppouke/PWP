import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from blokus import db
from blokus.models import *
from blokus.constants import *
from sqlalchemy.exc import IntegrityError
from blokus.utils import BlokusBuilder, create_error_response

class GameItem(Resource):
	# Get specified existing game resource.
    def get(self, game):
        db_game = Game.query.filter_by(handle=game).first()
        if db_game is None:
            return create_error_response(404, "Not found",
                "No game was found with the name {}".format(game)
            )

        body = BlokusBuilder(
                handle=db_game.handle,
                players=db_game.players,
                placed_blocks=db_game.placed_blocks
            )
        body.add_namespace("blokus", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.gameitem", game=game))
        body.add_control("profile", GAME_PROFILE)
        body.add_control_delete_game(db_game)
        body.add_control_add_player(db_game)
        body.add_control_get_games()

        body['players'] = []

        for db_player in Player.query.filter_by(game_id=db_game.id).all():
            item = BlokusBuilder(
                game_id =  db_player.game_id,
                color =  db_player.color,
                used_blocks =  db_player.used_blocks,
            )
            item.add_control("self", url_for("api.playeritem", game=db_game.handle, player=str(db_player.color)))
            item.add_control("profile", PLAYER_PROFILE)
            item.add_control("game", url_for("api.gameitem", game = db_game.handle))
            body['players'].append(item)
        return Response(json.dumps(body), 200, mimetype=MASON)

	# Add a player to an existing game
    def post(self, game):
        db_game = Game.query.filter_by(handle=game).first()
        if db_game == None:
            return create_error_response(
                404, "Not found",
                "No game was found with the handle {}".format(game)
            )
        if not request.json:
            return create_error_response(415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Player.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))


        db_player = Player.query.filter_by(game_id=db_game.id, color=request.json["color"]).first()
        if not db_player is None:
            return create_error_response(409, "Already exists",
            "Player with color '{}' already exists.".format(request.json["color"])
    )
        player = Player(
            color=request.json["color"]
        )

        try:
            db.session.add(player)
            db_game.players.append(player)
            db.session.commit()

        except IntegrityError:
            return create_error_response(409, "Already exists",
                "Player with color '{}' already exists.".format(request.json["color"])
            )

        return Response(status=201, headers={
            "Location": url_for("api.playeritem", player = str(request.json["color"]), game = db_game.handle)
        })

	# Delete an existing game resource
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
	# Get a list of existing games
    def get(self):
        body = BlokusBuilder()

        body.add_namespace("blokus", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.gamecollection"))
        body.add_control_get_blocks()
        body.add_control_get_transactions()
        body.add_control_add_game()
        body["items"] = []
        for game in Game.query.all():
            item = BlokusBuilder(
                handle=game.handle,
                players=game.players,
                placed_blocks = game.placed_blocks
            )
            item.add_control("self", url_for("api.gameitem", game=game.handle))
            item.add_control("profile", GAME_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)

	# Create a new game
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
            "Location": url_for("api.gameitem", game=request.json["handle"])
        })
