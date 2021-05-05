import pygame
import requests
import json
from dataclasses import dataclass

Colors = [(100, 100, 100), (200, 0, 0), (0, 200, 0), (0, 0, 200), (200, 200, 0)]
WINDOW_HEIGHT = 400
WINDOW_WIDTH = 600
BOARD_HEIGHT = 400
BOARD_WIDTH = 400

blocks = []
selectedBlock = -1
placeColor = 1
blockBuffer = []
placeShape = None
blockRotation = 0
usedBlocks = ""
myTurn = False
curTurn = '-'
finished = False

availableBlocks = []
blockSelection = 0

def LoadBlock(blockString):
    """
    Converts a string encoded (5x5 = 25) block into a 5x5 pygame image
    """
    global blockBuffer, placeShape
    blockBuffer = []
    for c in blockString:
        if c=="0":
            blockBuffer.append(0xFF)
            blockBuffer.append(0xFF)
            blockBuffer.append(0xFF)
            blockBuffer.append(0x00)
        elif c=="1" or c=="2" or c=="3" or c=="4":
            blockID = placeColor
            blockBuffer.append(Colors[blockID][0])
            blockBuffer.append(Colors[blockID][1])
            blockBuffer.append(Colors[blockID][2])
            blockBuffer.append(0x3F)
    placeShape = pygame.image.frombuffer(bytearray(blockBuffer), (5,5), 'RGBA')

def ScrollBlocks(dr):
    """
    Changes the selected block index by specified number.
    Loops around if above maximum or below 0 index.
    """
    global blockSelection, usedBlocks

    blockSelection = (blockSelection+dr) % len(availableBlocks)
    tries = 0
    while tries<len(availableBlocks):
        if not str(blockSelection) in usedBlocks:
            break
        blockSelection = (blockSelection+dr) % len(availableBlocks)
        tries += 1
    if not tries == len(availableBlocks):
        LoadBlock(availableBlocks[blockSelection])
        return True
    return False


def UpdateBoard(game_resource):
    """
    Updates displayed board with data from server
    """
    global blocks
    blocks = list(map(int,game_resource["placed_blocks"]))

def Ping(s, game_href):
    """
    Pings the game server for the current game state
    """
    global myTurn, placeColor, usedBlocks, curTurn
    game = getResource(s, game_href)
    curTurn = str(game['turn_information'])
    UpdateBoard(game)

    if myTurn == False and placeColor == int(game['turn_information']):
        myTurn = True
        for p in game['players']:
            if p['color'] == placeColor:
                usedBlocks = p['used_blocks'].split(',')
                break

def main(s, game_href, player_href):
    """
    Handles drawing and pygame events
    """
    global SCREEN, CLOCK, placeShape, blockBuffer, blockRotation, finished, myTurn
    running = True
    ScrollBlocks(0)
    pygame.init()
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    CLOCK = pygame.time.Clock()

    while running:
        SCREEN.fill((50,50,50))
        if pygame.time.get_ticks() % 2000 == 0:
            Ping(s, game_href)
        drawGrid()
        if not finished:
            SetSelection(pygame.mouse.get_pos())
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and myTurn==True:
                    SetBlock(s, game_href)
                    if not ScrollBlocks(1):
                        finished=True
                    myTurn=False
                if event.button == 4:
                    if not ScrollBlocks(-1):
                        finished=True
                elif event.button == 5:
                    if not ScrollBlocks(1):
                        finished=True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    blockRotation -= 90
                    if blockRotation < 0:
                        blockRotation += 360
                elif event.key == pygame.K_e:
                    blockRotation += 90
                    if blockRotation > 360:
                        blockRotation -= 360

def SetSelection(mouse):
    """
    Draws the chosen block on currently selected tile
    """
    global selectedBlock
    mouseBlock = (mouse[0]//20, mouse[1]//20)
    if mouseBlock[0] >= 20 or mouseBlock[1] >= 20:
        selectedBlock = (-1, -1)
    else:
        selectedBlock = (mouseBlock[0], mouseBlock[1])
        rotated = pygame.transform.rotate(placeShape, blockRotation)
        scaled = pygame.transform.scale(rotated, (98, 98))
        SCREEN.blit(scaled, ((mouseBlock[0]-2)*20+1, (mouseBlock[1]-2)*20+1))

def isCorner(pos):
    """
    Returns true if specified tile is in corner
    """
    if pos[0] == 0 or pos[0] == 19:
        return pos[1]==0 or pos[1]==19
    return False

def CornerAttached(pos):
    """
    Returns -1 if specified tile is side to side with own color
    Returns 0 if there is no connection to previous blocks of own color
    Returns 1 if tile is attached to a previous block of own color by corner
    """
    checks = [(-1,0),(1,0),(0,-1),(0,1)]
    for c in checks:
        checkPos = (pos[0]+c[0], pos[1]+c[1])
        blockIndex = checkPos[0] + checkPos[1]*20
        if checkPos[0] < 0 or checkPos[0] > 19 or checkPos[1] < 0 or checkPos[1] > 19:
            continue
        if blocks[blockIndex] == placeColor:
            return -1
    checks = [(-1,-1),(1,1),(1,-1),(-1,1)]
    for c in checks:
        checkPos = (pos[0]+c[0], pos[1]+c[1])
        blockIndex = checkPos[0] + checkPos[1]*20
        if checkPos[0] < 0 or checkPos[0] > 19 or checkPos[1] < 0 or checkPos[1] > 19:
            continue
        if blocks[blockIndex] == placeColor:
            return 1
    return 0
        
def SetBlock(s, game_href):
    """
    Checks if block placement is valid, then places it if so.
    First block by any color must cover a corner
    Future blocks must be attached to previous own blocks by a corner
    and must not be attached by a side
    """
    global placeColor, blockSelection
    selected = []
    firstTime = True
    for b in blocks:
        if b == placeColor:
            firstTime = False
            break
    
    rotated = pygame.transform.rotate(placeShape, blockRotation)
    st = bytearray(pygame.image.tostring(rotated, 'RGBA'))
    valid = True
    inCorner = False
    cornerAttached = False
    for i in range(25):
        pos = (i%5-2 + selectedBlock[0], i//5-2 + selectedBlock[1])
        blockIndex = pos[0] + pos[1]*20
        if st[i*4+3] > 0:
            if pos[0] < 0 or pos[0] > 19 or pos[1] < 0 or pos[1] > 19:
                valid = False
                break
            if isCorner((pos[0], pos[1])):
                inCorner = True
            if (CornerAttached(pos)==1 or firstTime):
                cornerAttached = True
            if blocks[blockIndex] == 0 and CornerAttached(pos)>-1:
                selected.append(blockIndex)
            else:
                valid = False
        #print(str(pos)+str(st[i*4+3]))
    if valid and cornerAttached and (not firstTime or inCorner):
        for b in selected:
            blocks[b] = placeColor
        placeBlock(s, game_href, placeColor, blockSelection, blocks)

def drawGrid():
    """
    Renders the current board and some text on the side
    """
    blockSize = 20 #Set the size of the grid block
    for x in range(0, BOARD_WIDTH, blockSize):
        for y in range(0, BOARD_HEIGHT, blockSize):
            pos = y+x//20
            c = Colors[blocks[pos]]
            rect = pygame.Rect(x+1, y+1, blockSize-2, blockSize-2)
            pygame.draw.rect(SCREEN, c, rect, 0)

    font_color=(255,255,255)
    font_obj=pygame.font.Font("C:\Windows\Fonts\segoeprb.ttf",25)
    # Render the objects
    text_obj=font_obj.render("Turn: "+curTurn,True,font_color)
    SCREEN.blit(text_obj,(BOARD_WIDTH, 10))
    text_obj=font_obj.render("Blocks left: "+str(len(availableBlocks)-len(usedBlocks)),True,font_color)
    SCREEN.blit(text_obj,(BOARD_WIDTH, 60))

API_URL = "http://127.0.0.1:5000/"
## Data classes for the resources
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
    """
    Error for api failing
    """
    def __init__(self, error_code, error_message):
        self.code = error_code
        self.message = error_message
        super().__init__(self.message)

def convert_value(value, schema_props):
    """
    Converts values to the integer.
    Copied from the lovelace exercise and edited to our needs
    """
    if schema_props["type"] == "integer":
        value = int(value)
    return value

def submit_data(s, ctrl, data):
    """
    Sends post or put request to the server
    Copied from the lovelace exercise 4
    """
    resp = s.request(
        ctrl["method"],
        API_URL + ctrl["href"],
        data=json.dumps(data),
        headers = {"Content-type": "application/json"}
    )
    return resp

def create_resource(s, tag, ctrl):
    """
    Posts resource to the server
    Copied from lovelace exercise 4
    """
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
    """
    Puts resource to the server
    Copied from the function above and edited to work with put
    """
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



def getBlocks(s, blocks_href):
    """
    Gets all blocks from the collection
    """
    resp = s.get(API_URL + blocks_href)
    body = resp.json()
    blocks = []
    for i in body['items']:
        r = s.get(API_URL + i['@controls']['self']['href'])
        b=r.json()
        blocks.append(b['shape'])
    return blocks

def getResource(s, href):
    """
    Gets resource from the server using its href
    """
    resp = s.get(API_URL + href)
    body = resp.json()
    return body

def getResourceFromLocation(s, location):
    """
    Gets resource from the server using its location gotten from post response
    """
    resp = s.get(location)
    body = resp.json()
    return body



def placeBlock(s, game_href, player_id, block_id, board):
    """
    Does transaction to the server to place a block
    """
    try:
        resp = s.get(API_URL + game_href)
        game_body = resp.json()
        player_list_id = -1
        print(game_body['players'])
        for i, p in enumerate(game_body['players']):
            if player_id == p['color']:
                player_list_id = i
                break
        print(player_list_id)
        next_player = game_body['players'][(player_list_id + 1) % len(game_body['players'])]['color']
        print(next_player)
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
        #Get the entrypoint
        s.headers.update({"Accept": "application/vnd.mason+json"})
        resp = s.get(API_URL + "/api/")
        if resp.status_code != 200:
            print("Unable to access API")
        else:
            #First get all the blocks from the server
            body = resp.json()
            availableBlocks = getBlocks(s, body['@controls']['blokus:blocks-all']['href'])

            #Get the game collection
            gameCollection = getResource(s, body['@controls']['blokus:games-all']['href'])

            #Select game from the list or create new game
            print("Select game or create new game:")
            i=1
            available_games = {}
            for g in gameCollection['items']:
                game = getResource(s, g['@controls']['self']['href'])
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
            #if choice==i player wants to create new game
            if choice==i:
                while True:
                    try:
                        #Create game resource
                        game_handle = input("Give name for the game: ")
                        
                        game_obj = Game(game_handle, "0"*400)
                        game_resource = create_resource(s, game_obj, gameCollection['@controls']['blokus:add-game'])
                        picked_game = getResourceFromLocation(s, game_resource)
                        
                        break
                    except APIError as e:
                        print("Error with code: {} and message: {}".format(e.code, e.message))
                pass
            else:
                #Get the selected game from the server
                picked_game = getResource(s, available_games[choice])
            print("Selected game: {}".format(picked_game['handle']))

            #Player selection
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

            #Send the player resource to the server
            player_obj = Player(color=player, used_blocks="")
            player_location = create_resource(s, player_obj, picked_game['@controls']['blokus:add-player'])

            player_resource = getResourceFromLocation(s, player_location)
            UpdateBoard(picked_game)
            
            placeColor = int(player_resource['color'])
            main(s, picked_game['@controls']['self']['href'], player_resource['@controls']['self']['href'])
