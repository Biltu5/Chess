""" 
This is the main driver file. It will be responsible for handling user input an displaying
displaying the Game state object.
"""
import pygame as p
import ChessEngine

WIDTH = HEIGHT = 512
DIMENTION = 8
SQ_SIZE = HEIGHT // DIMENTION # SQ_SIZE = Square size = 64
MAX_FPS = 15
IMAGES = {}

'''
Initialize a global dictionary of images . This will be called exactly once in the main.
'''
def loadImages():
    pieces = ['bR','bN','bB','bQ','bK','bB','bN','bR','bp','wR','wN','wB','wQ','wK','wB','wN','wR','wp']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("Images/"+piece+".png").convert_alpha(),(SQ_SIZE,SQ_SIZE))

    # Note : We can access an image by saying 'IMAGES['wp']'

'''
This is  main driver for our code .This will handle user input and updating the graphics .
'''
def main():
    p.init()
    p.display.set_caption('Chess -B Nayak')
    screen = p.display.set_mode((WIDTH,HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.gameState()
    validMoves = gs.getValidMoves()
    moveMade = False # Flag variable for when move is made 
    animate = False # Flag variable for when we should animate a move
    loadImages()
    running = True
    sqSelected = () # no squareis selected , keep track of the last click of the user (tuple(row,column))
    playerClicks = [] # keep track of player clicks [two tuple: [(6,4),(6,8)]]
    gameOver = False

    while running :
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False

            # Mouse Button Down
            elif event.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos() #get the mouse position as a tuple (x,y)
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE

                    if sqSelected == (row,col): # The user clicked twice
                        sqSelected = () # deselected the square
                        playerClicks = [] # clear player clicks
                    else:
                        sqSelected = (row,col)
                        playerClicks.append(sqSelected) # append for both first and second click

                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0],playerClicks[1],gs.board)
                        print(move.getChessNotaion())

                        for select_move in validMoves:
                            if move == select_move:
                                gs.makeMove(select_move)
                                moveMade = True
                                animate = True
                                sqSelected = () # Reset user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]

            # Key Button Down
            elif event.type == p.KEYDOWN:
                if event.key == p.K_z: #Undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                if event.key == p.K_r: #Reset the board when 'r' is pressed
                    gs = ChessEngine.gameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1],screen,gs.board,clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen,gs,validMoves,sqSelected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen,' Black Wins CHECKMATE')
            else:
                drawText(screen,' White Wins CHECKMATE')
        elif gs.staleMate:
            gameOver = True
            drawText(screen,' Stalemate')

        clock.tick(MAX_FPS)
        p.display.flip() # Update the full display Surface to the screen

'''
Highlight square selected and moves for piece selected
'''
def highlightSquares(screen,gs,validMoves,sqSelected):
    if sqSelected != ():
        r,c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): #Sqselected is a piece that can be moved
            # Highlight selected square
            s = p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100) # Transparenciv value -> 0 transparent : 255 oaque
            s.fill(p.Color('blue'))
            screen.blit(s,(c*SQ_SIZE, r*SQ_SIZE)) 
            # Highlight moves from tha square 
            s.fill(p.Color('green'))
            for move in validMoves:
                if move.startRow == r and move.startColumn == c:
                    screen.blit(s,(move.endColumn * SQ_SIZE, move.endRow * SQ_SIZE))

'''
Responsible for all the graphics for the current game state .
'''
def drawGameState(screen,gs,validMoves,sqSelected):
    drawBoard(screen) # draw squares on the board 
    highlightSquares(screen,gs,validMoves,sqSelected)
    drawPieces(screen,gs.board) # draw pieces on top of these squares

'''
Draw the squares on the board . The top left square is always light.
'''
def drawBoard(screen):
    global colors 
    colors = [p.Color('white'),p.Color('grey')]
    for r in range(DIMENTION):
        for c in range(DIMENTION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE)) # Rect(left,top,width,height)

'''
Draw the Pieces on the board using the current gameState.board 
'''
def drawPieces(screen,board):
    for r in range(DIMENTION):
        for c in range(DIMENTION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE)) #blit (image,position on screen)

'''
Animating a move
'''
def animateMove(move,screen,board,clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endColumn - move.startColumn
    framesPerSquare = 10 # Frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r,c = (move.startRow + dR * frame / frameCount, move.startColumn + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen,board)
        # erase the piece from its ending square
        color = colors[(move.endRow + move.endColumn) % 2]
        endSquare = p.Rect(move.endColumn * SQ_SIZE , move.endRow * SQ_SIZE , SQ_SIZE , SQ_SIZE)
        p.draw.rect(screen,color,endSquare)
        # Draw capture pieceonto rectangle
        if move.pieceCapture != '--':
            screen.blit(IMAGES[move.pieceCapture],endSquare)
        # Draw moving piece
        screen.blit(IMAGES[move.pieceMoved],p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip() # Update the full display Surface to the screen
        clock.tick(60)

def drawText(screen, text):
    font = p.font.SysFont("Halvitca",32, True, False)
    textObject = font.render(text, 0 , p.Color('grey'))
    textLocation = p.Rect(0,0,WIDTH,HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2 , HEIGHT / 2 -  textObject.get_height() / 2)
    screen.blit(textObject , textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2,2))

if __name__ == '__main__':
    main()