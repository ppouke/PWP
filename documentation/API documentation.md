FORMAT: 1A
HOST: http://localhost:5000/

# HTTPBlokus API

This API enables users to play games of Blokus online. The API serves JSON data extended by the [Mason hypermedia format](https://github.com/JornWildt/Mason).

# Group Link Relations

This section described custom link relations defined in this API. These are not resources. The API also uses
[IANA link relations](http://www.iana.org/assignments/link-relations/link-relations.xhtml) where applicable. Custom link relations are CURIEs that use the blokus prefix.

## add-game

This is a control that is used to add a game to the game collection. The control includes a JSON schema and must be accessed with POST.

## games-all

Leads to the root level game collection which is a list of all game instances on the server.

## game

Leads to the game related to specific player


## blocks-all

Leads to the list of all blocks included in the game.

## delete

Deletes the associated resource. Must be accessed with DELETE

# Group Profiles

This section includes resource profiles which provide semantic descriptions for the attributes of each resource, as well as the list of controls (by link relation) available from that resource.

## Game Profile

Profile definition for all game related resources.

### Link Relations

This section lists all possible link relations associated with games; not all of them are necessarily present on each resource type. The following link relations from the blokus namespace are used:

 * [add-game](reference/link-relations/add-game)
 * [games-all](reference/link-relations/games-all)
 * [delete](reference/link-relations/delete)
 * [blocks-all](reference/link-relations/blocks-all)

The following [IANA RFC5988](http://www.iana.org/assignments/link-relations/link-relations.xhtml) link relations are also used:

 * collection
 * edit
 * profile
 * self
 * item

### Semantic Descriptors

#### Data Type Game

 * `Name`: Name of the of game. Mandatory.


## Player Profile

Profile definition for all player related resources.

### Link Relations

This section lists all possible link relations associated with Players; not all of them are necessarily present on each resource type. The following link relations from the blokus namespace are used:

 * [game](reference/link-relations/game)

The following [IANA RFC5988](http://www.iana.org/assignments/link-relations/link-relations.xhtml) link relations are used:

 * edit
 * self
 * profile

### Semantic Descriptors

#### Data Type Player

 * `color`: The color of the player as a integer. The client can determine a color based on the ingeter.
 * `available-blocks`: Available blocks for that player. Comma separated list in string.

## Block Profile

Profile definition for all block related resources.

### Link Relations

This section lists all possible link relations associated with Block; not all of them are necessarily present on each resource type. The following link relations from the blokus namespace are used:

 * [blocks-all](reference/link-relations/blocks-all)
 * [games-all](reference/link-relations/games-all)

The following [IANA RFC5988](http://www.iana.org/assignments/link-relations/link-relations.xhtml) link relations are also used:

 * self
 * item
 * collection

### Semantic Descriptors

#### Data Type Block

 * `shape`: The shape of the block encoded as a string. Mandatory.

## Error Profile

Profile definition for all errors returned by the API. See [Mason error control](https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md#property-name-error) for more information about errors.

+ Attributes

    + resource_url (string, required) - URI of the resource the error was generated from.

# Group Entry

This group contains the entry point of the API

## Entry Point [/api/]

### Get entry point [GET]

Get the API entry point

+ Request

    + Headers

            Accept: application/vnd.mason+json

+ Response 200 (application/vnd.mason+json)

    + Body

            {
                "@namespaces": {
                    "blokus": {
                        "name": "/blokus/link-relations#"
                    }
                },
                "@controls": {
                    "blokus:games-all": {
                        "href": "/api/games/"
                    },
                    "blokus:blocks-all": {
                        "href": "/api/blocks/"
                    }
                }
            }


# Group Games

Group artists description

## Games Collection [/api/games/?sortby={field}]

Collection of all games running on the server.

+ Parameters

    + field (string, optional) - Field to use for sorting

        + Default: `name`
        + Members

            + `name`
            + `unique_name`

### List all games [GET]

Get a list of all games running on the server

+ Relation: games-all
+ Request

    + Headers

            Accept: application/vnd.mason+json

+ Response 200 (application/vnd.mason+json)

    + Body

            {
                "@namespaces": {
                    "blokus": {
                      "name": "http://wherever.this.server.is/blokus/link-relations#"
                    }
                },
                "@controls": {
                    "blokus:add-game": {
                      "href": "/api/games/",
                      "method": "POST",
                      "schema": {
                            "type": "object",
                            "properties": {
                              "name": {
                                "description": "Game name",
                                "type": "string"
                              },
                            "unique_name": {
                            "description": "Game name in lowercase, whitespaces replaced with underscore",
                            "type": "string"
                            },
                            "turn_information": {
                            "description": "Turn information as integer",
                            "type": integer
                            },
                            "blocks": {
                            "description": "Placed blocks, encoded as 20x20 char string",
                            "type": "string"
                            }
                        },
                        "required": ["name", "unique_name","turn_information","blocks"]
                    },
                    "blokus:blocks-all" :{
                        "href" : "/api/blocks/"
                    }
                }
                },
                "items": [
                    {
                      "name": "Casual game",
                      "unique_name": "casual_game",
                      "player_count": 4,
                      "@controls": {
                          "self": {
                          "href": "/api/games/casual_game/"
                          },
                          "profile": {
                          "href": "/profiles/game/"
                          }
                    }
                ]
            }

### Add game [POST]

Add a game to the game collection.

+ Relation: add-game
+ Request (application/json)

    + Headers

            Accept: application/vnd.mason+json

    + Body

            {
                "name": "Casual game",
                "unique_name": "casual_game",
                "blocks" : "424022000343044301300102430202322221423310112120034120020320403
                        2331300402433021314011401012343101403003220034001434110101133312421
                        0243410101433322400324014234343310123141242411221044213114233134411
                        3330344102440433022401022031313400243323131233201034022432001232402
                        4140020214304242043221402213203341443042412442131132444300200000424
                        3204212411331121311331012312222342130433124044413310134222042120400",
                "turn_information": 1
            }

+ Response 400 (application/vnd.mason+json)

        The client is trying to send a JSON document that doesn't validate against the schema, or has non-existent release date.

+ Response 415 (application/vnd.mason+json)

        The client did not use the proper content type, or the request body was not valid JSON.

## Game [/api/games/{game}/]

Information about an artist

+ Parameters

    + game: casual_game (string) - game's unique name (unique_name)

### Game information [GET]

Get the game representation.

+ Relation: self
+ Request

    + Headers

            Accept: application/vnd.mason+json

+ Response 200 (application/vnd.mason+json)

    + Body

            {
            "@namespaces": {
              "blokus": {
                "name": "http://wherever.this.server.is/blokus/link-relations#"
              }
            },
            "@controls": {
              "add-player": {
                "href": "/api/games/casual_game/",
                "method": "POST",
                "schema": {
                  "type": "object",
                  "properties": {
                        "color": {
                          "description": "Players color id",
                          "type": "integer"
                        },
                        "available-blocks": {
                            "description" : "blocks available to the player",
                            "type" : "string"
                        }
                    },
                    "required": ["color", "available-blocks"]
                }
            },
            "blokus:delete": {
                "href": "/api/games/casual_game/",
                "method": "DELETE"
            },
                "collection": {
                "href": "/api/games/"
            },
            "self": {
            "href" : "/api/game/casual_game/"
            },
            "profile" : {
            "href" : "/profiles/game/"
            }
            
            },
            "name": "Casual Game",
            "unique_name": "casual_game",
            "blocks" : "424022000343044301300102430202322221423310112120034120020320403
                        2331300402433021314011401012343101403003220034001434110101133312421
                        0243410101433322400324014234343310123141242411221044213114233134411
                        3330344102440433022401022031313400243323131233201034022432001232402
                        4140020214304242043221402213203341443042412442131132444300200000424
                        3204212411331121311331012312222342130433124044413310134222042120400",
            "turn_information": 1
            }

### Delete game [DELETE]

Deletes the game and players.

+ Relation: delete
+ Request

    + Headers

            Accept: application/vnd.mason+json

+ Response 204

+ Response 404 (application/vnd.mason+json)

    The client is trying to delete a game that doesn't exist.

    + Body

            {
                "resource_url": "/api/games/casual_game/",
                "@error": {
                    "@message": "Game not found",
                    "@messages": [null]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }

### Add player [POST]

Add a player to the game. Must validate against the player schema.

+ Relation: add-player
+ Request (application/json)

    + Headers

            Accept: application/vnd.mason+json

    + Body

            {
            "color": 1,
            "available-blocks": "1,2,3,4,5,6,7,8,9,10,11,12,13"
            }

+ Response 204


+ Response 400 (application/vnd.mason+json)

    The client is trying to send a JSON document that doesn't validate against the schema, or color index is invalid.

    + Body

            {
                "resource_url": "/api/games/casual_game/",
                "@error": {
                    "@message": "Invalid color number",
                    "@messages": [
                        "Color number must be between 1-4"
                    ]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }

+ Response 404 (application/vnd.mason+json)

    The client is trying to add player to a game that doesn't exist

    + Body

            {
                "resource_url": "/api/games/casual_game/",
                "@error": {
                    "@message": "Game not found",
                    "@messages": [null]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }

+ Response 415 (application/vnd.mason+json)

    The client sent a request with the wrong content type or the request body was not valid JSON.

    + Body

            {
                "resource_url": "/api/games/casual_game/",
                "@error": {
                    "@message": "Unsupported media type",
                    "@messages": [
                        "Use JSON"
                    ]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }


### Edit Game [PUT]

Add a game to the game collection.

+ Relation: edit
+ Request (application/json)

    + Headers

            Accept: application/vnd.mason+json

    + Body

            {
                "name": "Casual Game",
                "unique_name": "casual_game",
                "blocks": "424022000343044301300102430202322221423310112120034120020320403
                                2331300402433021314011401012343101403003220034001434110101133312421
                                0243410101433322400324014234343310123141242411221044213114233134411
                                3330344102440433022401022031313400243323131233201034022432001232402
                                4140020214304242043221402213203341443042412442131132444300200000424
                                3204212411331121311331012312222342130433124044413310134222042120400",
                "turn_information": 1
            }

+ Response 400 (application/vnd.mason+json)

        The client is trying to send a JSON document that doesn't validate against the schema, or has non-existent release date.

+ Response 415 (application/vnd.mason+json)

        The client did not use the proper content type, or the request body was not valid JSON.

# Group Player

## Player [/api/players/{player}/]

Information about the specified player

+ Parameters

    + player: 1 (integer) - player's unique id

### Player information [GET]

Get the player representation.

+ Relation: self
+ Request

    + Headers

            Accept: application/vnd.mason+json

+ Response 200 (application/vnd.mason+json)

    + Body

            {
            "@namespaces": {
                "blokus": {
                "name": "http://wherever.this.server.is/blokus/link-relations#"
                }
            },
            "@controls": {
              "self":{
                "href": "/api/players/1/"
            }
                        "profile": {
            "href": "/profiles/player/"
            }
              "edit": {
                "href": "/api/players/1/",
                "method": "PUT"
                            "schema": {
                  "type": "object",
                  "properties": {
                    "color": {
                      "description": "Players color id",
                      "type": "integer"
                    }
            "available-blocks": "1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13"
                  },
                  "required": ["color", "available-blocks"]
                }
                        "game": {
            "href": "/api/games/casual_game/
            }
            
              }
            },
            "color": 1
            "available-blocks": "1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13"
            }


### Edit player [PUT]

Edit the player resource

+ Relation: edit
+ Request (application/json)

    + Headers

            Accept: application/vnd.mason+json

    + Body

            {
                "color": 2
                "available-blocks": "1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13"
            }


+ Response 400 (application/vnd.mason+json)

    The client is trying to send a JSON document that doesn't validate against the schema.

    + Body

            {
                "resource_url": "/api/players/1/",
                "@error": {
                    "@message": "color is not an integer",
                    "@messages": [
                        "color must be integer between 1 and 4"
                    ]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }

+ Response 404 (application/vnd.mason+json)

    The client is trying to edit a player that doesn't exist.

    + Body
    
            {
                "resource_url": "/api/players/1/",
                 "@error": {
                    "@message": "Player not found",
                    "@messages": [null]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }

+ Response 415 (application/vnd.mason+json)

    The client sent a request with the wrong content type or the request body was not valid JSON.

    + Body
    
            {
                "resource_url": "/api/players/1/",
                "@error": {
                    "@message": "Unsupported media type",
                    "@messages": [
                        "Use JSON"
                    ]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }

# Group Block

## Block Collection [/api/blocks/]

Collection of all blocks known the server.

### List all blocks [GET]

Get a list of all blocks known to the server

+ Relation: blocks-all
+ Request

    + Headers

            Accept: application/vnd.mason+json

+ Response 200 (application/vnd.mason+json)

    + Body

            {
              "@namespaces": {
                "blokus": {
                  "name": "http://wherever.this.server.is/blokus/link-relations#"
                }
              },
                "items": [
                    {
                        "shape": "1010101010101010101010101",
                        "@controls":
                        {
                        "self": {
                        "href": "/api/blocks/1/"
                        }
                        "profile":
                        {
                        "href": "/profiles/block/"
                        }
                        "blokus:games-all"
                        {
                        "href": "/api/games/
                        }
                    }
                ]
            }


## Block [/api/blocks/{block}]

### Block information [GET]

Get the block representation.

+ Relation: self
+ Request

    + Headers
    
            Accept: application/vnd.mason+json

+ Response 200 (application/vnd.mason+json)

    + Body

            {
            "@namespaces": {
              "blokus": {
                "name": "http://wherever.this.server.is/blokus/link-relations#"
              }
            },
            "@controls": {
            "self : {
            "href": "/api/blocks/1/"
            },
              "collection": {
                "href": "/api/blocks/"
              },
            "profile": {
            "href": "/profiles/block/"
            }
            },
            "shape": "1010101010101010101010101"
            }


