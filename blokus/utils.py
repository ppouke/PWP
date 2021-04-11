
import json
from flask import Response, request, url_for
from blokus.constants import *
from blokus.models import *

class MasonBuilder(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.

        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.

        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.

        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, href, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.

        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md

        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href

class BlokusBuilder(MasonBuilder):

    def add_control_delete_game(self, game):
        self.add_control(
            "blokus:delete",
            url_for("api.gameitem", game=game),
            method="DELETE",
            title="Delete this game"
        )

    def add_control_add_game(self):
        self.add_control(
            "blokus:add-game",
            url_for("api.gamecollection"),
            method="POST",
            encoding="json",
            title="Add a new game",
            schema=Game.get_schema()
        )

    def add_control_get_games(self):
        self.add_control(
            "blokus:games-all",
            url_for("api.gamecollection"),
            method="GET",
            title="Get list of games"
        )

    def add_control_get_game(self, game):
        self.add_control(
            "blokus:gameitem",
            url_for("api.gamecollection", game=game),
            method="GET",
            title="Get a game"
        )

    def add_control_get_blocks(self):
        self.add_control(
            "blokus:blocks-all",
            url_for("api.blockcollection"),
            method="GET",
            title="Get list of existing blocks"
        )

    def add_control_add_player(self, game):
        self.add_control(
            "blokus:add-player",
            url_for("api.gameitem", game=game),
            method="POST",
            encoding="json",
            title="Add a new player to a game",
            schema=Player.get_schema()
        )

    def add_control_add_transaction(self):
        self.add_control(
            "blokus:add-transaction",
            url_for("api.transactionfactory"),
            method="POST",
            encoding="json",
            title="Add transaction into game",
            schema=Transaction.get_schema()
        )

    def add_control_edit_transaction(self, transaction):
        self.add_control(
            "edit",
            url_for("api.transactionitem", transaction=transaction),
            method="PUT",
            encoding="json",
            title="Edit this transaction",
            schema=Transaction.get_schema()
        )

    def add_control_get_transactions(self):
        self.add_control(
            "blokus:transactions-all",
            url_for("api.transactionfactory"),
            method="GET",
            title="Get all transactions"
        )

    def add_control_delete_transaction(self, transaction):
        self.add_control(
            "blokus:delete",
            url_for("api.transactionitem", transaction=transaction),
            method="DELETE",
            title="Delete this transaction"
        )

def create_error_response(status_code, title, message=None):
    resource_url = request.path
    body = MasonBuilder(resource_url=resource_url)
    body.add_error(title, message)
    body.add_control("profile", href=ERROR_PROFILE)
    return Response(json.dumps(body), status_code, mimetype=MASON)
