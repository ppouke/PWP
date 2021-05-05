import json
import os
import pytest
import tempfile
import time
from datetime import datetime
from jsonschema import validate
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

from blokus import create_app, db
from blokus.models import *




@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle

# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def client():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }

    app = create_app(config)

    with app.app_context():
        db.create_all()
        _populate_db()

    yield app.test_client()

    os.close(db_fd)
    os.unlink(db_fname)

def _populate_db():
    player = Player(
        color=1,
        used_blocks=""
    )
    game = Game(handle="game-1", placed_blocks="0"*400)
    block = Block(shape=("00000"
                        "00000"
                        "00100"
                        "00000"
                        "00000")
    )
    trans = Transaction()

    trans.game = game
    trans.player = player

    game.players.append(player)

    db.session.add(player)
    db.session.add(game)
    db.session.add(block)
    db.session.add(trans)
    db.session.commit()


def _get_game_json(number=2):
    """
    Creates a valid game JSON object to be used for PUT tests.
    """
    return {"handle": "game-{}".format(number)}

def _get_player_json(number=2):
    """
    Creates a valid player JSON object to be used for PUT tests.
    """
    return {"color": number}

def _get_transaction_json(player = 1, game=1):
    """
    Creates a valid transaction JSON object to be used for PUT tests.
    """
    return {"player": player, "game" : "game-{}".format(game) }

def _get_block_json():
    """
    Creates a valid block JSON object to be used for PUT tests.
    """
    return {"shape":"0"*25}

def _check_namespace(client, response):
    """
    Checks that the "blokus" namespace is found from the response body, and
    that its "name" attribute is a URL that can be accessed.
    """

    ns_href = response["@namespaces"]["blokus"]["name"]
    resp = client.get(ns_href)
    assert resp.status_code == 200

def _check_control_get_method(ctrl, client, obj):
    """
    Checks a GET type control from a JSON object be it root document or an item
    in a collection. Also checks that the URL of the control can be accessed.
    """

    href = obj["@controls"][ctrl]["href"]
    resp = client.get(href)
    assert resp.status_code == 200


def _check_control_delete_method(ctrl, client, obj):
    """
    Checks a DELETE type control from a JSON object be it root document or an
    item in a collection. Checks the contrl's method in addition to its "href".
    Also checks that using the control results in the correct status code of 204.
    """

    href = obj["@controls"][ctrl]["href"]
    method = obj["@controls"][ctrl]["method"].lower()
    assert method == "delete"
    resp = client.delete(href)
    assert resp.status_code == 204

def _check_control_put_method(ctrl, client, obj, tested):
    """
    Checks a PUT type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid game/player/transaction against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 204.
    """

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "put"
    assert encoding == "json"
    body = None
    if tested == "game":
        body = _get_game_json()
    elif tested == "player":
        body = _get_player_json()
    elif tested == "transaction":
        body = _get_transaction_json()
    elif tested == "block":
        body = _get_block_json()
    body["name"] = obj["name"]
    validate(body, schema)
    resp = client.put(href, json=body)
    assert resp.status_code == 204

def _check_control_post_method(ctrl, client, obj, tested):
    """
    Checks a POST type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid game/player/transaction against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 201.
    """

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "post"
    assert encoding == "json"
    body = None
    if tested == "game":
        body = _get_game_json()
    elif tested == "player":
        body = _get_player_json()
    elif tested == "transaction":
        body = _get_transaction_json()
    elif tested == "block":
        body = _get_block_json()
    validate(body, schema)
    resp = client.post(href, json=body)
    assert resp.status_code == 201


class TestBlockCollection(object):
    """
    This class tests all the possible methods for the Block collection (get, post)
    """
    RESOURCE_URL = "/api/blocks/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        assert len(body["items"]) == 1
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)

    def test_post(self, client):
        valid = _get_block_json()

        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        #assert resp.headers["Location"].endswith(self.RESOURCE_URL + "1" + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200



class TestBlockItem(object):
    """
    This class tests all the possible methods for the Block item (get, put, delete)
    """
    RESOURCE_URL = "/api/blocks/1/"
    INVALID_URL = "/api/block/#/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("blokus:blocks-all", client, body)

        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        valid = _get_block_json()


        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # test with wrong content type
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        # test with valid
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204


    def test_delete(self, client):
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404


class TestGameCollection(object):
    """
    This class tests all the possible methods for the Game collection (get, post)
    """
    RESOURCE_URL = "/api/games/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_post_method("blokus:add-game", client, body, "game")
        assert len(body["items"]) == 1
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)


    def test_post(self, client):
        valid = _get_game_json()

        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + valid["handle"] + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200

        # send same data again for 409
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409




class TestGameItem(object):
    """
    This class tests all the possible methods for the Game item (get, post, delete)
    """
    RESOURCE_URL = "/api/games/game-1/"
    INVALID_URL = "/api/games/game-x/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_get_method("self", client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("blokus:games-all", client, body)
        _check_control_delete_method("blokus:delete", client, body)
        _check_control_get_method("blokus:transactions-all", client, body)
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404


    def test_delete(self, client):
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404

    def test_post(self, client):
        valid = _get_player_json(2)

        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + "players/" + str(valid["color"]) + "/")
        print(resp.headers["Location"])
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200

        # send same data again for 409
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409


class TestPlayerItem(object):
    """
    This class tests all the possible methods for the Player item(get)
    """
    RESOURCE_URL = "/api/games/game-1/players/1/"
    INVALID_URL = "/api/games/game-1/players/wrong/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("self", client, body)
        _check_control_get_method("game", client, body)

        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

class TestTransactionFactory(object):
    """
    This class tests all the possible methods for the Transaction factory (get, post)
    """
    RESOURCE_URL = "/api/transactions/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_post_method("blokus:add-transaction", client, body, "transaction")
        assert len(body["items"]) == 1
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)


    def test_post(self, client):
        valid = _get_transaction_json()

        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + "2/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200


        #test with invalid game
        valid = _get_transaction_json(game = 5)
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 404

        #test with invalid player
        valid = _get_transaction_json(player = 2)
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 404


        #test with invalid next player
        valid["player"] = 1
        valid["next_player"] = 2
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 404

        #test with valid next player
        valid["next_player"] = 1
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201

        # remove model field for 400
        valid.pop("game")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

class TestTransactionItem(object):
    """
    This class tests all the possible methods for the Transaction item (get, put, delete). It also checks if the game and player resources are changed correctly
    """
    RESOURCE_URL = "/api/transactions/1/"
    INVALID_URL = "/api/transactions/bobsyouruncle/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("self", client, body)

        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        valid = _get_transaction_json()

        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        # test with valid (only change model)

        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204


        #test with invalid game
        valid = _get_transaction_json(game = 5)
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 404

        #test with invalid player
        valid = _get_transaction_json(player = 2)
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 404


        #test with invalid next player
        valid["player"] = 1
        valid["next_player"] = 2
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 404

        #test with valid next player
        valid["next_player"] = 1
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204


        #commit
        valid["commit"] = 1
        valid["used_blocks"] = "111"
        valid["placed_blocks"] = "1"*400
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 202

        #check if resources were changed correctly
        resp = client.get("/api/games/game-1/players/1")
        assert resp.json["used_blocks"] == "111"
        resp = client.get("/api/games/game-1")
        assert resp.json["placed_blocks"] == "1"*400


        # remove field for 400
        valid.pop("player")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400







    def test_delete(self, client):
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404
