import pygame

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

def LoadBlock(blockString):
    global blockBuffer, placeShape
    blockBuffer = []
    for c in blockString:
        if c=="0":
            blockBuffer.append(0xFF)
            blockBuffer.append(0xFF)
            blockBuffer.append(0xFF)
            blockBuffer.append(0x00)
        elif c=="1" or c=="2" or c=="3" or c=="4":
            blockID = int(c)
            blockBuffer.append(Colors[blockID][0])
            blockBuffer.append(Colors[blockID][1])
            blockBuffer.append(Colors[blockID][2])
            blockBuffer.append(0x3F)
    placeShape = pygame.image.frombuffer(bytearray(blockBuffer), (5,5), 'RGBA')

def Init():
    global blocks
    blocks = []
    for i in range(20*20):
        blocks.append(0)
        
    LoadBlock("00000"
              "01100"
              "00100"
              "00110"
              "00000")

def main():
    global SCREEN, CLOCK, placeShape, blockBuffer, blockRotation
    running = True
    pygame.init()
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    CLOCK = pygame.time.Clock()

    while running:
        SCREEN.fill((50,50,50))
        drawGrid()
        SetSelection(pygame.mouse.get_pos())
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
            elif event.type == pygame.MOUSEBUTTONUP:
                SetBlock()
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
    if pos[0] == 0 or pos[0] == 19:
        return pos[1]==0 or pos[1]==19

def CornerAttached(pos):
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
        
def SetBlock():
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

def drawGrid():
    blockSize = 20 #Set the size of the grid block
    for x in range(0, BOARD_WIDTH, blockSize):
        for y in range(0, BOARD_HEIGHT, blockSize):
            pos = y+x//20
            c = Colors[blocks[pos]]
            rect = pygame.Rect(x+1, y+1, blockSize-2, blockSize-2)
            pygame.draw.rect(SCREEN, c, rect, 0)

Init()
main()
