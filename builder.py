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
            api.url_for(Game, game=game),
            method="DELETE",
            title="Delete this game"
        )

    def add_control_add_game(self):
        self.add_control(
            "blokus:add-game",
            api.url_for(GameCollection),
            method="POST",
            title="Add a new game"
        )

    def add_control_get_games(self):
        self.add_control(
            "blokus:games-all",
            api.url_for(GameCollection),
            method="GET",
            title="Get list of games"
        )

    def add_control_get_blocks(self):
        self.add_control(
            "blokus:blocks-all",
            api.url_for(BlockCollection),
            method="GET",
            title="Get list of existing blocks"
        )

    def add_control_add_player(self, game):
        self.add_control(
            "blokus:add-player",
            api.url_for(Game, game=game),
            method="POST",
            title="Add a new player to a game"
        )
