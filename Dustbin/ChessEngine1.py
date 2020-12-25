"""
This  class is responsible for storing the all the information about the current state of a class game .
It will also be responsible for detarmining the valid move at the curret state.It will also keep a move log.
"""
class gameState:
    def __init__(self):
        # Board is an 8x8 2D list ,each element of the list has 2 character.
        # The first character is represent color of the piece and second 
        # character represent types of the piece . Where '--' represents a 
        # empty space with no piece .
        self.board = [
            ['bR','bN','bB','bQ','bK','bB','bN','bR'],
            ['bp','bp','bp','bp','bp','bp','bp','bp'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['wp','wp','wp','wp','wp','wp','wp','wp'],
            ['wR','wN','wB','wQ','wK','wB','wN','wR']]

        self.moveFunctions = {'p':self.getPawnMoves,'R':self.getRookMoves,'N':self.getKnightMoves,
                               'Q':self.getQueenMoves,'K':self.getKingMoves,'B':self.getBishopMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7,4) #White king tracks
        self.blackKingLocation = (0,4) #Black king tracks
        self.inCheck = False
        self.pins = []
        self.checks = []

    '''
    Takes a move as a parameter and executes it (This will not work for casteling, pawn pomotion and en-passant)
    '''
    def makeMove(self,move):
        self.board[move.startRow][move.startColumn] = "--"
        self.board[move.endRow][move.endColumn] = move.pieceMoved
        self.moveLog.append(move) # log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove # swap players
        # Update the king position if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow,move.endColumn)
        if move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow,move.endColumn)

    '''
    Undo the last move made
    '''
    def undoMove(self):
        if len(self.moveLog) != 0: # Make sure that there is a moved to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startColumn] = move.pieceMoved
            self.board[move.endRow][move.endColumn] = move.pieceCapture
            self.whiteToMove = not self.whiteToMove # switch turns back
            # Update the king's position when it needed
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow,move.startColumn)
            if move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow,move.startColumn)

    '''
    All moves considering checks 
    '''
    def getValidMoves(self):
        moves = []
        self.incheck, self.pins,self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingrow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingrow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.inCheck) == 1: # Only one check, then block check or move king
                moves = self.getAllPossibleMoves()
                # to block a check you must move a piece into one of your square between the enemy piece and king
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol] # Enemy piece causing the check
                validSquares = [] # squares that pieces can move to
                # If knight , must capture knight or move king , Other pieces can be block
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow,checkCol)]
                else:
                    for i in range(1,8):
                        validSquare = (kingrow + check[2] * i, kingCol + check[3] * i) # check[2] & check[3] are check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol: ## Once you get to piece and checks
                            break
                    # Get rid of any moves that don't block check or move king
                    for i in range(len(moves)-1,-1,-1) : #Go through backwards when you are removing from a list as iterating
                        if moves[i].pieceMoved[i] != 'K': # Move does not move king so it must block or capture 
                            if not (move[i].endRow,move[i].endColumn) in validSquares: # Move does not block check or capture piece
                                moves.remove(moves[i])
            else: # Double check , King has to move
                self.getKingMoves(kingrow,kingCol,moves)
        else: # Not in checks , So all moves are fine
            moves = self.getAllPossibleMoves()
        
        return moves

    '''
    Returns if the player is in check , a list of pins , and a list of checks
    '''
    def checkForPinsAndChecks(self):
        pins = [] # Squares where the allide pinned piece and direction pinned from
        checks = [] # Squares where enemy is applying a check
        inCheck = False
        if self.whiteToMove :
            enemyColor = 'b'
            allyColor = 'w'
            startRow = self.whiteKingLocation[0]
            startColumn = self.whiteKingLocation[1]
        else:
            enemyColor = 'w'
            allyColor = 'b'
            startRow = self.blackKingLocation[0]
            startColumn = self.blackKingLocation[1]
        # Check outward from king for pins and checks, keep track to pins
        directions = ((-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = () # reset possible pin
            for i in range(1,8):
                endRow = startRow + d[0] * i
                endColumn = startColumn + d[1] * i
                if 0 <= endRow < 8 and 0 <= endColumn < 8 :
                    endPiece = self.board[endRow][endColumn]
                    if endPiece[0] == allyColor:
                        if possiblePin == (): #1st allied piece could be pinned 
                            possiblePin = (endRow,endColumn,d[0],d[1])
                        else: # 2nd allied piece , so no pin or check possible in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        # 5 Possibilities here in this complex condiction
                        #1. Orthogonally away from king and piece is a rook
                        #2. Diagonally away from king and piece is a bishop
                        #3. 1 square away diagonally from king and piece is pawn 
                        #4. any direction and piece is a queen 
                        #5. Any direction 1 square away and piece is a king (This is necessary to prevent a king move to a square controlled by another king)
                        if (0 <= j <= 3 and type == 'R') or 
                        

    '''
    Determine if the enemy can attack the square r,c
    '''
    def squareUnderAttack(self,r,c):
        self.whiteToMove = not self.whiteToMove # Switch to opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove # Switch return back
        for move in oppMoves:
            if move.endRow == r and move.endColumn == c: # square is under attack
                return True
        return False

    '''
    All moves without considering checks
    '''
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): # Number of rows of the board
            for c in range(len(self.board[r])): # Number of columns in given rows
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves) # Calls the appropriate move functions based on piece type
        return moves

    ''' 
    get all the pawn moves for the pawn located at row,col and these moves to the list
    '''
    def getPawnMoves(self,r,c,moves):
        if self.whiteToMove: # White pawn moves
            if self.board[r-1][c] == "--": #1 square pawn advance
                moves.append(Move((r,c),(r-1,c),self.board))
                if r == 6 and self.board[r-2][c] == "--": #2 square pawn advance
                    moves.append(Move((r,c),(r-2,c),self.board))
            if c-1 >= 0: # Capture enemy piece to the Left
                if self.board[r-1][c-1][0] == 'b': 
                    moves.append(Move((r,c),(r-1,c-1),self.board))
            if c+1 <= 7: # Capture to the right 
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r,c),(r-1,c+1),self.board))
        else: # Black pawn moves
            if self.board[r+1][c] == "--": #1 square pawn advance
                moves.append(Move((r,c),(r+1,c),self.board))
                if r == 1 and self.board[r+2][c] == "--": #2 square pawn advance
                    moves.append(Move((r,c),(r+2,c),self.board))
            if c-1 >= 0: # Capture enemy piece to the Left
                if self.board[r+1][c-1][0] == 'w': 
                    moves.append(Move((r,c),(r+1,c-1),self.board))
            if c+1 <= 7: # Capture to the right 
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r,c),(r+1,c+1),self.board))
        #Add pawn promotion and en-plazent rule later          

    '''
    get all the rook moves for the rook located at row,col and these moves to the list
    '''
    def getRookMoves(self,r,c,moves):
        direction = ((-1,0),(0,-1),(1,0),(0,1)) #Up , Left , Down , Right
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in direction:
            for i in range(1,8):
                endRow = r + d[0] * i
                endColumn = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endColumn < 8: # Check selected square on board or not
                    endPiece = self.board[endRow][endColumn]
                    if endPiece == "--":  # Empty space valid
                        moves.append(Move((r,c),(endRow,endColumn),self.board))
                    elif endPiece[0] == enemyColor: # Enemy piece valid
                        moves.append(Move((r,c),(endRow,endColumn),self.board))
                        break
                    else: # Frienly piece invalid
                        break
                else: # outside of the board
                    break

    '''
    get all the Bishop moves for the Bishop located at row,col and these moves to the list
    '''
    def getBishopMoves(self,r,c,moves):
        direction = ((-1,-1),(-1,1),(1,-1),(1,1)) #Up , Left , Down , Right diagonal
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in direction:
            for i in range(1,8):
                endRow = r + d[0] * i
                endColumn = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endColumn < 8: # Check selected square on board or not
                    endPiece = self.board[endRow][endColumn]
                    if endPiece == "--":  # Empty space valid
                        moves.append(Move((r,c),(endRow,endColumn),self.board))
                    elif endPiece[0] == enemyColor: # Enemy piece valid
                        moves.append(Move((r,c),(endRow,endColumn),self.board))
                        break
                    else: # Frienly piece invalid
                        break
                else: # outside of the board
                    break

    '''
    get all the Knight moves for the Knight located at row,col and these moves to the list
    '''
    def getKnightMoves(self,r,c,moves):
        direction = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)) #Up , Left , Down , Right diagonal
        friendColor = 'w' if self.whiteToMove else 'b'
        for d in direction:
            endRow = r + d[0] 
            endColumn = c + d[1]
            if 0 <= endRow < 8 and 0 <= endColumn < 8: # Check selected square on board or not
                endPiece = self.board[endRow][endColumn]
                if endPiece[0] != friendColor: # Enemy piece and empty space valid
                    moves.append(Move((r,c),(endRow,endColumn),self.board))

    '''
    get all the King moves for the King located at row,col and these moves to the list
    '''
    def getKingMoves(self,r,c,moves):
        direction = ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)) #Up , Left , Down , Right diagonal
        friendColor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = r + direction[i][0] 
            endColumn = c + direction[i][1]
            if 0 <= endRow < 8 and 0 <= endColumn < 8: # Check selected square on board or not
                endPiece = self.board[endRow][endColumn]
                if endPiece[0] != friendColor: # Enemy piece and empty space valid
                    moves.append(Move((r,c),(endRow,endColumn),self.board))

    '''
    get all the Queen moves for the Queen located at row,col and these moves to the list
    '''
    def getQueenMoves(self,r,c,moves):
        self.getRookMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)

class Move:
    # maps keys to values
    # key : value
    ranksToRows = {"1" : 7, "2" : 6, "3" : 5, "4" : 4,
                   "5" : 3, "6" : 2, "7" : 1,"8" : 0}
    rowsToRanks = {v: k for k , v in ranksToRows.items()}
    filesToCols = {"a" : 0, "b" : 1, "c" : 2, "d" : 3,
                   "e" : 4, "f" : 5, "g" : 6, "h" : 7}
    colsToFiles = {v: k for k ,v in filesToCols.items()}

    def __init__(self,startSq,endSq,board):
        self.startRow = startSq[0]
        self.startColumn = startSq[1]
        self.endRow = endSq[0]
        self.endColumn = endSq[1]
        self.pieceMoved = board[self.startRow][self.startColumn]
        self.pieceCapture = board[self.endRow][self.endColumn]
        self.moveId = self.startRow * 1000 + self.startColumn * 100 + self.endRow * 10 + self.endColumn
        #print(self.moveId)

    '''
    Overriding the equals method
    '''
    def __eq__(self,other): # Bug shikar
        if isinstance(other,Move):
            return self.moveId == other.moveId
        return False

    def getChessNotaion(self):
        # You can make this like real chess notation (0,0) to (0,3) --> (a8+a4)
        return((self.colsToFiles[self.startRow] + self.rowsToRanks[self.startColumn]) + ' + ' +
               (self.colsToFiles[self.endRow] + self.rowsToRanks[self.endColumn]))