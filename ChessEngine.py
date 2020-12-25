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
        self.checkMate = False
        self.staleMate = False
        self.enPassantPossible = () # Co-ordinates for the square where where en-Passant is Possible
        self.currentCastlingRight = CastleRights(True,True,True,True) # In the biginning of the game we can castle in any side so all are true
        self.castleRightLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

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
        
        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endColumn] = move.pieceMoved[0] + 'Q'
        
        
        # If an enPassant Move, must update the board to capture the pawn
        if move.isEnPassantMove:
            self.board[move.startRow][move.endColumn] = '--' # capturing the pawn
            print(f'start Row :{move.startRow}, End column :{move.endColumn}')
        
        # If pawn moves twice , next move can capture enpassant
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: # Only on 2 square pawn advances
            self.enPassantPossible = ((move.startRow + move.endRow)//2,move.startColumn)
        else:
            self.enPassantPossible = ()

        # Castle move
        if move.isCastleMove:
            if move.endColumn - move.startColumn == 2: # King side castle move
                self.board[move.endRow][move.endColumn - 1] = self.board[move.endRow][move.endColumn +1] # Moves the rook
                self.board[move.endRow][move.endColumn + 1] = '--' # Erase the old rook
            else: # Queen side castle move
                self.board[move.endRow][move.endColumn + 1] = self.board[move.endRow][move.endColumn - 2] # Moves the rook
                self.board[move.endRow][move.endColumn - 2] = '--' # Erase the old rook

        # Update castling rights -> whenever it is a rook or king move
        self.updateCastleRights(move)
        self.castleRightLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

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

            # Undo enpassant
            if move.isEnPassantMove:
                self.board[move.endRow][move.endColumn] = '--' # Removes the pawn that was added in the wrong square
                self.board[move.startRow][move.endColumn] = move.pieceCapture # puts the pawn back on the correct square it was capture from
                self.enPassantPossible = (move.endRow,move.endColumn) # Allow an en-passant to happen on the next move

            # When undo a 2 square pawn advance should make enPassantPossible = () again
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enPassantPossible = ()
            
            # Undo castling rights
            self.castleRightLog.pop() # Get rid of the row castle rights from the move we are undoing
            newRights = self.castleRightLog[-1] # select the current castle rights to the last one in the list
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)

            # Undo castle move
            if move.isCastleMove:
                if move.endColumn - move.startColumn == 2: # King side
                    self.board[move.endRow][move.endColumn + 1] = self.board[move.endRow][move.endColumn - 1] # Rook is back to old position
                    self.board[move.endRow][move.endColumn - 1] = '--' # So Erase rook
                else: # Queen side
                    self.board[move.endRow][move.endColumn - 2] = self.board[move.endRow][move.endColumn + 1]
                    self.board[move.endRow][move.endColumn + 1] = '--'

    '''
    Update castle right
    '''
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startColumn == 0: # Left Rook
                    self.currentCastlingRight.wqs = False
                elif move.startColumn == 7: # right Rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startColumn == 0: # Left Rook
                    self.currentCastlingRight.bqs = False
                elif move.startColumn == 7: # right Rook
                    self.currentCastlingRight.bks = False

    '''
    All moves considering checks 
    '''
    def getValidMoves(self):
        tempEnPassantPossible = self.enPassantPossible
        tempcastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        #1. Generate all possible moves
        moves = self.getAllPossibleMoves() 

        #2. For each move , make a move
        for i in range(len(moves)-1,-1,-1): # When removing from a list go backwords through this list
            self.makeMove(moves[i])
            #3. Generate all opponent moves
            #4. For each you'r opponent moves, see if they attack your king 
            self.whiteToMove = not self.whiteToMove
            if self.incheck():
                #5. If they do attack your king, not a valid move
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        
        if len(moves) == 0: # Either checkmate or stalemate
            if self.incheck():
                self.checkMate = True
                print('checkmate')
            else:
                print('stalemate')
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
  
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0],self.whiteKingLocation[1],moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
            
        self.enPassantPossible = tempEnPassantPossible   
        self.currentCastlingRight = tempcastleRights   
        return moves

    '''
    Determine if the current player is in check
    '''
    def incheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0],self.blackKingLocation[1])

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
            if self.board[r - 1][c] == "--": #1 square pawn advance
                moves.append(Move((r, c),(r - 1, c),self.board))
                if r == 6 and self.board[r - 2][c] == "--": #2 square pawn advance
                    moves.append(Move((r, c),(r-2, c),self.board))
            if c-1 >= 0: # Capture enemy piece to the Left
                if self.board[r-1][c-1][0] == 'b': 
                    moves.append(Move((r,c),(r-1,c-1),self.board))
                elif (r-1,c-1) == self.enPassantPossible:
                    moves.append(Move((r,c),(r-1,c-1),self.board,isEnPassantMove = True))
            if c+1 <= 7: # Capture to the right 
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r,c),(r-1,c+1),self.board))
                elif (r-1,c+1) == self.enPassantPossible:
                    moves.append(Move((r,c),(r-1,c+1),self.board, isEnPassantMove = True))
        else: # Black pawn moves
            if self.board[r+1][c] == "--": #1 square pawn advance
                moves.append(Move((r,c),(r+1,c),self.board))
                if r == 1 and self.board[r+2][c] == "--": #2 square pawn advance
                    moves.append(Move((r,c),(r+2,c),self.board))
            if c-1 >= 0: # Capture enemy piece to the Left
                if self.board[r+1][c-1][0] == 'w': 
                    moves.append(Move((r,c),(r+1,c-1),self.board))
                elif (r+1,c-1) == self.enPassantPossible:
                    moves.append(Move((r,c),(r+1,c-1),self.board, isEnPassantMove = True))
            if c+1 <= 7: # Capture to the right 
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r,c),(r+1,c+1),self.board))
                elif (r+1,c+1) == self.enPassantPossible:
                    moves.append(Move((r,c),(r+1,c+1),self.board, isEnPassantMove = True))       

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

    '''
    Generate all valid castle moves for the king at (r,c) and add them to the list of moves
    '''
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r,c):
            return # Can't castle while we are in check
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingSideCastleMoves(r,c,moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueenSideCastleMoves(r,c,moves)

    def getKingSideCastleMoves(self, r ,c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--': # Check right side and 2nd right side of the king is '--'
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2): # king not in check
                moves.append(Move((r,c),(r,c+2),self.board, isCastleMove = True))

    def getQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--' :
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r,c),(r,c-2),self.board, isCastleMove = True))

class CastleRights:
    def __init__(self,wks,bks,wqs,bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move:
    # maps keys to values
    # key : value
    ranksToRows = {"1" : 7, "2" : 6, "3" : 5, "4" : 4,
                   "5" : 3, "6" : 2, "7" : 1,"8" : 0}
    rowsToRanks = {v: k for k , v in ranksToRows.items()}
    filesToCols = {"a" : 0, "b" : 1, "c" : 2, "d" : 3,
                   "e" : 4, "f" : 5, "g" : 6, "h" : 7}
    colsToFiles = {v: k for k ,v in filesToCols.items()}

    def __init__(self,startSq,endSq,board,isEnPassantMove = False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startColumn = startSq[1]
        self.endRow = endSq[0]
        self.endColumn = endSq[1]
        self.pieceMoved = board[self.startRow][self.startColumn]
        self.pieceCapture = board[self.endRow][self.endColumn]
        
        # For Pawn promotion
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
        
        # For an en-passant
        self.isEnPassantMove = isEnPassantMove
        if self.isEnPassantMove:
            self.pieceCapture = 'wp' if  self.pieceMoved == 'bp' else 'bp'

        # For Castle Moved
        self.isCastleMove = isCastleMove


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
        return((self.colsToFiles[self.startRow] + self.rowsToRanks[self.startColumn]) + 
               (self.colsToFiles[self.endRow] + self.rowsToRanks[self.endColumn]))