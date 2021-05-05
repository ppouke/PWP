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
        """
        Returns list of all transactions in the database and a link for adding transactions
        """
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
            item.add_control("self", url_for("api.transactionitem", transaction=str(db_trans.id)))
            item.add_control("profile", TRANSACTION_PROFILE)

            item.add_control_get_game(db_trans.game.handle)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self):
        """
        Adds new Transaction to the database
        """
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
        #Check that valid game has been given
        if "game" in request.json:
            db_game = Game.query.filter_by(handle=request.json["game"]).first()
            if db_game is None:
                return create_error_response(
                    404, "Not found",
                    "No game was found with the handle {}".format(request.json["game"])
                )
            transaction.game = db_game
            
        #Check if valid player has been given
        if "player" in request.json:
            color = int(request.json["player"])

            db_player = Player.query.filter_by(game_id=transaction.game.id, color=color).first()
            if db_player is None:
                return create_error_response(
                    404, "Not found",
                    "No player was found with the id {}".format(request.json["player"])
                )
            transaction.player = db_player
        #Check if valid next player has been given
        if "next_player" in request.json:
            color = int(request.json["next_player"])
            if(color>-1):
                db_player = Player.query.filter_by(game_id=transaction.game.id, color=color).first()
                if db_player is None:
                    return create_error_response(
                        404, "Not found",
                        "No player was found with the id {}".format(request.json["player"])
                    )
                transaction.next_player = color
        #Get the initial placed and used blocks from the database
        transaction.placed_blocks = transaction.game.placed_blocks
        transaction.used_blocks = transaction.player.used_blocks


        id = str(transaction.id)
        try:
            db.session.add(transaction)
            db.session.commit()
        except IntegrityError:
            pass
        print("Players in post")
        print(transaction.game.players)
        id = str(transaction.id)
        return Response(status=201, headers={
            "Location": url_for("api.transactionitem", transaction=id)
        })


class TransactionItem(Resource):
    
    def get(self, transaction):
        """
        Returns specific transaction from the database
        """
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
        """
        Updates specific transaction in the database. If variable "commit" is 1 then commits the changes
        """
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
        #Check if the game is valid
        if "game" in request.json:
            db_game = Game.query.filter_by(handle=request.json["game"]).first()
            if db_game is None:
                return create_error_response(
                    404, "Not found",
                    "No game was found with the handle {}".format(request.json["game"])
                )
            db_trans.game = db_game
        #Check if the player is valid
        if "player" in request.json:
            color = int(request.json["player"])

            db_player = Player.query.filter_by(game_id= db_trans.game_id, color=color).first()
            if db_player is None:
                return create_error_response(
                    404, "Not found",
                    "No player was found with the id {}".format(request.json["player"])
                )
            db_trans.player = db_player
        #Check if the next player is valid
        if "next_player" in request.json:
            color = int(request.json["next_player"])

            db_player_2 = Player.query.filter_by(game_id= db_trans.game_id, color=color).first()
            if db_player_2 is None:
                return create_error_response(
                    404, "Not found",
                    "No player was found with the id {}".format(request.json["player"])
                )
            db_trans.next_player = color
            
        #Get the placed blocks and used blocks from the request
        if "placed_blocks" in request.json:
            db_trans.placed_blocks = request.json["placed_blocks"]
        if "used_blocks" in request.json:
            db_trans.used_blocks = request.json["used_blocks"]
        
        #If commit is 1 then commit changes to the Game and Player resources in the database
        commited = False
        if "commit" in request.json:
            if int(request.json["commit"]) == 1:
                next_player = Player.query.filter_by(id = db_trans.next_player).first()
                if db_trans.game is None or db_trans.player is None or next_player is None:
                    return create_error_response(
                        400, "Bad request",
                        "No player or game was assigned for the transaction")
                commited=True
                db_trans.game.placed_blocks = db_trans.placed_blocks
                db_trans.game.turn_information = db_trans.next_player
                db_trans.player.used_blocks = db_trans.used_blocks
                

                

        try:
            db.session.commit()
        except Exception as e:
            print(e)
        if commited:
            return Response(status=202)
        else:
            return Response(status=204)

    def delete(self, transaction):
        """
        Deletes specific transaction from the database
        """
        db_trans = Transaction.query.filter_by(id=transaction).first()
        if db_trans == None:
            return create_error_response(
                404, "Not found",
                "No transaction was found with the id {}".format(transaction)
            )

        db.session.delete(db_trans)
        db.session.commit()

        return Response(status=204)
