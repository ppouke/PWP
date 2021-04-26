import pygame
import requests
from dataclasses import dataclass
import json
from time import sleep


blocks = []
@dataclass
class Player:
    color: int
    used_blocks: str

@dataclass
class Game:
    handle: str
    placed_blocks: str

@dataclass
class Transaction:
    game: str
    player: int
    next_player: int = -1
    placed_blocks: str = "0"*400
    used_blocks: str = ""
    commit: int = 0


class APIError(Exception):
    def __init__(self, error_code, error_message):
        self.code = error_code
        self.message = error_message
        super().__init__(self.message)
def convert_value(value, schema_props):
    if schema_props["type"] == "integer":
        value = int(value)
    return value

def submit_data(s, ctrl, data):
    resp = s.request(
        ctrl["method"],
        API_URL + ctrl["href"],
        data=json.dumps(data),
        headers = {"Content-type": "application/json"}
    )
    return resp

def create_resource(s, tag, ctrl):
    body = {}
    schema = ctrl["schema"]
    
    for name, props in schema["properties"].items():
        value = getattr(tag, name)
        if value is not None:
            value = convert_value(value, props)
            body[name] = value
    
    resp = submit_data(s, ctrl, body)
    if resp.status_code == 201:
        return resp.headers["Location"]
    else:
        print("Error")
        raise APIError(resp.status_code, resp.content)

def edit_resource(s, tag, ctrl):
    body = {}
    schema = ctrl["schema"]
    
    for name, props in schema["properties"].items():
        value = getattr(tag, name)
        if value is not None:
            value = convert_value(value, props)
            body[name] = value
    print("-----{}".format(json.dumps(body,indent=4)))
    resp = submit_data(s, ctrl, body)
    if resp.status_code == 204:
        return 204
    else:
        print("Error")
        raise APIError(resp.status_code, resp.content)

API_URL = "http://127.0.0.1:5000/"

def getBlocks(s, blocks_href):
    resp = s.get(API_URL + blocks_href)
    body = resp.json()
    blocks = []
    for i in body['items']:
        r = s.get(API_URL + i['@controls']['self']['href'])
        b=r.json()
        blocks.append(b['shape'])
    return blocks

def getResource(s, href):

    resp = s.get(API_URL + href)
    body = resp.json()
    return body

def getResourceFromLocation(s, location):
    resp = s.get(location)
    body = resp.json()
    return body

def getGame(s, href):
    resp = s.get(API_URL + href)
    return resp.json()

def placeBlock(s, game_href, player_id, block_id, board):
    try:
        resp = s.get(API_URL + game_href)
        game_body = resp.json()
        player_list_id = -1
        for i, p in enumerate(game_body['players']):
            if player_id == p['color']:
                player_list_id = i
                break

        next_player = game_body['players'][(player_list_id + 1) % len(game_body['players'])]['color']
        trans_resp = s.get(API_URL + game_body['@controls']['blokus:transactions-all']['href'])
        trans_body = trans_resp.json()

        trans_obj = Transaction(game_body['handle'], player_id, next_player)
        trans_location = create_resource(s, trans_obj, trans_body['@controls']['blokus:add-transaction'])

        trans_resource = getResourceFromLocation(s,trans_location)
        trans_obj.used_blocks = trans_resource['used_blocks'] + "{},".format(block_id)
        trans_obj.placed_blocks = "".join(map(str, board))
        trans_obj.next_player = next_player
        trans_obj.commit = 1
        edit_resource(s, trans_obj, trans_resource['@controls']['edit'])
        resp = s.get(API_URL + game_href)
        game_body = resp.json()
        return game_body
    except APIError as e:
        print(e.code)
        




if __name__ == "__main__":
    with requests.Session() as s:
        s.headers.update({"Accept": "application/vnd.mason+json"})
        resp = s.get(API_URL + "/api/")
        if resp.status_code != 200:
            print("Unable to access API")
        else:
            body = resp.json()
            blocks = getBlocks(s, body['@controls']['blokus:blocks-all']['href'])

            gameCollection = getResource(s, body['@controls']['blokus:games-all']['href'])
            print("Select game or create new game:")
            i=1
            available_games = {}
            for g in gameCollection['items']:
                game = getGame(s, g['@controls']['self']['href'])
                if len(game['players'])<4:
                    print("{}. {}".format(i,g['handle']))
                    available_games[i] = g['@controls']['self']['href']
                    i += 1
            
            print("{}. New game".format(i))
            choice = -1
            while True:
                try:
                    choice = int(input("Choice (1-{}): ".format(i)))
                    if choice>0 and choice<i+1:
                        break
                except ValueError:
                    continue
                print("Error: Give choice between 1-{}".format(i))
            

            picked_game = {}
            if choice==i:
                while True:
                    try:
                        game_handle = input("Give name for the game: ")
                        
                        game_obj = Game(game_handle, "0"*400)
                        game_resource = create_resource(s, game_obj, gameCollection['@controls']['blokus:add-game'])
                        picked_game = getResourceFromLocation(s, game_resource)
                        
                        break
                    except APIError as e:
                        print("Error with code: {} and message: {}".format(e.code, e.message))
                pass
            else:
                picked_game = getGame(s, available_games[choice])
            print("Selected game: {}".format(picked_game['handle']))
            player = -1
            available_players = [1,2,3,4]
            for p in picked_game['players']:
                available_players.remove(int(p['color']))
            
            while True:
                try:
                    player = int(input("Select player number ({}): ".format(available_players)))
                    if player in available_players:
                        break
                except ValueError:
                    continue
                print("Error: Pick valid player number")
            print("Selected player: {}".format(player))
            player_obj = Player(color=player, used_blocks="")
            player_resource = create_resource(s, player_obj, picked_game['@controls']['blokus:add-player'])

            print(json.dumps(placeBlock(s, picked_game['@controls']['self']['href'], player, 0, "1"*400),indent=4))
