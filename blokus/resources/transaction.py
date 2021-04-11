import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from blokus import db
from blokus.models import *
from blokus.constants import *
from blokus.utils import BlokusBuilder, create_error_response
from sqlalchemy.exc import IntegrityError

class TransactionFactory(Resource):
    def get(self):
        body = BlokusBuilder()
        body.add_namespace("blokus", LINK_RELATIONS_URL)

        body.add_control("self", url_for("api.transactionfactory"))
        body.add_control_add_transaction()

        body["items"] = []
        for db_trans in Transaction.query.all():
            item = BlokusBuilder(
                used_blocks = db_trans.used_blocks,
                board_state = db_trans.board_state
            )
            item.add_control("self", url_for("api.transactionitem", transaction=db_trans.id))
            item.add_control("profile", TRANSACTION_PROFILE)

            item.add_control_get_game(db_trans.game.handle)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self):
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Transaction.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        transaction = Transaction()

        if "game" in request.json:
            db_game = Game.query.filter_by(handle=request.json["game"]).first()
            if db_game is None:
                return create_error_response(
                    404, "Not found",
                    "No game was found with the handle {}".format(request.json["game"])
                )
            transaction.game = db_game

        if "player" in request.json:
            color = int(request.json["player"])
            if transaction.game is None:
                return create_error_response(
                    404, "Not found",
                    "No game was assigned for the transaction".format(request.json["game"])
                )
            db_player = Player.query.filter_by(game_id=transaction.game.id, color=color).first()
            if db_player is None:
                return create_error_response(
                    404, "Not found",
                    "No player was found with the id {}".format(request.json["player"])
                )
            transaction.player = db_player

        if "next_player" in request.json:
            color = int(request.json["next_player"])
            if transaction.game is None:
                return create_error_response(
                    404, "Not found",
                    "No game was assigned for the transaction".format(request.json["game"])
                )
            db_player = Player.query.filter_by(game_id=transaction.game.id, color=color).first()
            if db_player is None:
                return create_error_response(
                    404, "Not found",
                    "No player was found with the id {}".format(request.json["player"])
                )
            transaction.next_player = db_player

        if "board_state" in request.json:
            transaction.board_state = request.json["board_state"]
        if "used_blocks" in request.json:
            transaction.board_state = request.json["used_blocks"]

        
        id = transaction.id
        try:
            db.session.add(transaction)
            db.session.commit()
        except IntegrityError:
            pass

        return Response(status=201, headers={
            "Location": url_for("api.transactionitem", transaction=id)
        })


class TransactionItem(Resource):
    def get(self, transaction):
        db_trans = Transaction.query.filter_by(id=transaction).first()
        if db_trans == None:
            return create_error_response(
                404, "Not found",
                "No transaction was found with the id {}".format(transaction)
            )

        body = BlokusBuilder(
            used_blocks = db_trans.used_blocks,
            board_state = db_trans.board_state
        )
        body.add_namespace("blokus", LINK_RELATIONS_URL)

        body.add_control("self", url_for("api.transactionitem", transaction=transaction))
        body.add_control("profile", TRANSACTION_PROFILE)
        body.add_control_edit_transaction(transaction)
        body.add_control_delete_transaction(transaction)
        body.add_control_get_game(db_trans.game.handle)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, transaction):
        db_trans = Transaction.query.filter_by(id=transaction).first()
        if db_trans == None:
            return create_error_response(
                404, "Not found",
                "No transaction was found with the id {}".format(transaction)
            )

        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Transaction.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        if "game" in request.json:
            db_game = Game.query.filter_by(handle=request.json["game"]).first()
            if db_game is None:
                return create_error_response(
                    404, "Not found",
                    "No game was found with the handle {}".format(request.json["game"])
                )
            db_trans.game = db_game

        if "player" in request.json:
            if db_trans.game is None:
                return create_error_response(
                    404, "Not found",
                    "No game was assigned for the transaction".format(request.json["game"])
                )
            color = int(request.json["player"])

            db_player = Player.query.filter_by(game_id=db_trans.game, color=color).first()
            if db_player is None:
                return create_error_response(
                    404, "Not found",
                    "No player was found with the id {}".format(request.json["player"])
                )
            db_trans.player = db_player

        if "next_player" in request.json:
            color = int(request.json["next_player"])

            db_player = Player.query.filter_by(color=color).first()
            if db_player is None:
                return create_error_response(
                    404, "Not found",
                    "No player was found with the id {}".format(request.json["player"])
                )
            db_trans.next_player = db_player

        if "board_state" in request.json:
            db_trans.board_state = request.json["board_state"]
        if "used_blocks" in request.json:
            db_trans.board_state = request.json["used_blocks"]

        if request.json["commit"] == 1:
            if db_trans.game is None or db_trans.player is None:
                return create_error_response(
                    400, "Bad request",
                    "No player or game was assigned for the transaction")
            db_trans.game.board_state = db_trans.board_state
            db_trans.game.turn_information = db_trans.next_player
            db_trans.player.used_blocks = db_trans.used_blocks

        db.session.commit()

        return Response(status=204)

    def delete(self, transaction):
        db_trans = Transaction.query.filter_by(id=transaction).first()
        if db_trans == None:
            return create_error_response(
                404, "Not found",
                "No transaction was found with the id {}".format(transaction)
            )

        db.session.delete(db_trans)
        db.session.commit()

        return Response(status=204)
