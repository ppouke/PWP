import pygame

Colors = [(100, 100, 100), (200, 0, 0), (0, 200, 0), (0, 0, 200), (200, 200, 0)]
WINDOW_HEIGHT = 400
WINDOW_WIDTH = 600
BOARD_HEIGHT = 400
BOARD_WIDTH = 400

blocks = []
selectedBlock = -1
placeColor = 1

def Init():
    global blocks
    blocks = []
    for i in range(20*20):
        blocks.append(0)

def main():
    global SCREEN, CLOCK
    running = True
    pygame.init()
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    CLOCK = pygame.time.Clock()
    SCREEN.fill((50,50,50))

    while running:
        SetSelection(pygame.mouse.get_pos())
        drawGrid()
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                SetBlock()

def SetSelection(mouse):
    global selectedBlock
    mouse = (mouse[0]//20, mouse[1]//20)
    if mouse[0] >= 20 or mouse[1] >= 20:
        selectedBlock = -1
    else:
        selectedBlock = mouse[0]+mouse[1]*20

def SetBlock():
    if selectedBlock >= 0:
        if blocks[selectedBlock] == 0:
            blocks[selectedBlock] = placeColor

def drawGrid():
    blockSize = 20 #Set the size of the grid block
    for x in range(0, BOARD_WIDTH, blockSize):
        for y in range(0, BOARD_HEIGHT, blockSize):
            pos = y+x//20
            c = Colors[blocks[pos]]
            if blocks[pos]==0 and pos==selectedBlock:
                c = (80,80,80)
            rect = pygame.Rect(x+1, y+1, blockSize-2, blockSize-2)
            pygame.draw.rect(SCREEN, c, rect, 0)

Init()
main()
