import blokus.models
import blokus.utils
from flask import url_for

class GameCollection(Resource):

    def get(self):
        body = BlokusBuilder()

        body.add_namespace("blokus", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.GameCollection"))
        body.add_control_get_blocks()
        body["items"] = []
        for game in Game.query.all():
            item = BlokusBuilder(
                handle=game.handle,
                players=game.players,
                board_state=game.board_state
            )
            item.add_control("self", api.url_for(GameItem, game=game.id))
            item.add_control("profile", GAME_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)
