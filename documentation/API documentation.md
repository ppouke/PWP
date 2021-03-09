FORMAT: 1A
HOST: http://localhost:5000/

# HTTPBlokus API

This API enables users to play games of Blokus online. The API serves JSON data extended by the [Mason hypermedia format](https://github.com/JornWildt/Mason).

# Group Link Relations

TODO
This section described custom link relations defined in this API. These are not resources. The API also uses 
[IANA link relations](http://www.iana.org/assignments/link-relations/link-relations.xhtml) where applicable. Custom link relations are CURIEs that use the mumeta prefix. 

## add-game

This is a control that is used to add a game to the game collection. The control includes a JSON schema and must be accessed with POST. 

## game

Leads to the game resource.

## games-all

Leads to the root level game collection which is a list of all game instances on the server.

## player

Leads to the chosen player resource within the game.

## current-player

Leads to the player resource of the current player in the game state.

## place-block

TODO: is it possible access two different resources with one control?
Places the chosen block that a player has on the board.

## edit

Edits the associated resource. Must be accessed with PUT

## delete

Deletes the associated resource. Must be accessed with DELETE

# Group Profiles

This section includes resource profiles which provide semantic descriptions for the attributes of each resource, as well as the list of controls (by link relation) available from that resource.

## Album Profile

Profile definition for all album related resources.

### Link Relations

This section lists all possible link relations associated with albums; not all of them are necessarily present on each resource type. The following link relations from the mumeta namespace are used:

 * [add-album](reference/link-relations/add-album)
 * [add-track](reference/link-relations/add-track)
 * [albums-all](reference/link-relations/albums-all)
 * [albums-va](reference/link-relations/albums-va)
 * [artists-all](reference/link-relations/artists-all)
 * [delete](reference/link-relations/delete)
 
The following [IANA RFC5988](http://www.iana.org/assignments/link-relations/link-relations.xhtml) link relations are also used:

 * author
 * collection
 * edit
 * profile
 * self
 
### Semantic Descriptors

#### Data Type Album

 * `title`: The albums title as it is written on the release, including capitalization and punctuation. Titles are unique per artist, and are used to address album resources. Mandatory.
 * `release`: Album's release date in [ISO 8601 format](https://www.iso.org/iso-8601-date-and-time-format.html) (YYYY-MM-DD). Use 01 for month or day if not known. Mandatory.
 * `artist`: The album's artist's name (null for VA albums), including capitalization and pucntuation.
 * `discs`: Number of discs the album contains. Default is 1.
 * `genre`: The albums musical genre as a string. Optional.

## Error Profile

Profile definition for all errors returned by the API. See [Mason error control](https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md#property-name-error) for more information about errors.

+ Attributes

    + resource_url (string, required) - URI of the resource the error was generated from. 
 
## Track Profile

Profile definition for all track related resources.

### Link Relations

This section lists all possible link relations associated with tracks; not all of them are necessarily present on each resource type. The following link relations from the mumeta namespace are used:

 * [albums-by](reference/link-relations/albums-by)
 * [delete](reference/link-relations/delete)
 
The following [IANA RFC5988](http://www.iana.org/assignments/link-relations/link-relations.xhtml) link relations are also used:

 * author
 * edit
 * profile
 * self
 * up

### Semantic Descriptors

#### Data Type Track

 * `title`: The track's title as it is written on the release, including capitalization and punctuation. Not unique. Mandatory.
 * `artist`: The track artist's name which is either the album artist, or the track's artist on VA albums.
 * `length`: Track length as a time in [ISO 8601 format](https://www.iso.org/iso-8601-date-and-time-format.html) (hh:mm:ss). Mandatory.
 * `disc_number`: Number of the disc of the album this track is on. Default is 1. Unique together with track number per album.
 * `track_number`: Number of the track on the disc it's on. Mandatory. Unique together with disc number per album. 
 
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
                    "mumeta": {
                        "name": "/musicmeta/link-relations#"
                    }
                },
                "@controls": {
                    "mumeta:albums-all": {
                        "href": "/api/albums/"
                    },
                    "mumeta:artists-all": {
                        "href": "/api/artists/"
                    }
                }
            }


# Group Artists

Group artists description

## Artist Collection [/api/artists/]

Collection of all artists

+ Parameters

    + field (string, optional) - Field to use for sorting
    
        + Default: `name`
        + Members
        
            + `name`
            + `unique_name`
            + `location`
            + `formed`
            + `disbanded`
			
### List all artists [GET]

Get a list of all artists

+ Relation: artists-all
+ Request

    + Headers
    
            Accept: application/vnd.mason+json

+ Response 200 (application/vnd.mason+json)
    
    + Body
	
		{
			"@namespaces": {
				"mumeta": {
					"name": "http://wherever.this.server.is/musicmeta/link-relations#"
				}
			},
			"@controls": {
				"mumeta:add-artist": {
					"href": "/api/artists/",
					"method": "POST",
					"schema": {
						"type": "object",
						"properties": {
							"name": {
								"description": "Artist name",
								"type": "string"
							},
							"unique_name": {
								"description": "Artist name in lowercase",
								"type": "string"
							},
							"location": {
								"description": "Artist origin",
								"type": "string"
							},
							"formed": {
								"description": "Date on which the artist came to be",
								"type": "string",
								"pattern": "^[0-9]{4}-[01][0-9]-[0-3][0-9]$"
							},
							"disbanded": {
								"description": "Date on which the artist was disbanded",
								"type": "string",
								"pattern": "^[0-9]{4}-[01][0-9]-[0-3][0-9]$"
							}
						},
						"required": ["name", "unique_name"]
					}
				},
				"mumeta:albums-all": {
					"href": "/api/albums/"
				}
			},
			"items": [
				{
				"name": "Scandal",
				"unique_name": "scandal",
				"location": "Osaka, JP",
				"formed": "2006-08-21",
				"disbanded": null,
				"@controls": {
					"self": {
						"href": "/api/artists/scandal/"
						}
					}
				}
			]
		}