import numpy as np

def betterPlacement(board, moves:tuple, player):
    ''' Takes a list of potential moves and determines which one is best based on moveQuality
    list can be of any size '''
    if len(moves) == 1:
        return moves[0]
    
    elif len(moves) > 1:
        bestMove = moves[0]
        bestQuality = moveQuality(board, bestMove[0], bestMove[1], player)
        for move in moves:
            quality = moveQuality(board, move[0], move[1], player)
            if quality > bestQuality:
                bestMove = move
                bestQuality = quality
        return bestMove

def orderMoves(myBoard, mySlicedBoard, evMoves, extraMoves, player=1):
    ''' Orders the moves based on the highest board balance value each of them provides, from largest to smallest'''
    move_scores = []
    
    for slicedMove in evMoves:
        # Transform the move from sliced board coordinates to full board coordinates
        fullBoardMove = boardMoveTransformer(myBoard, mySlicedBoard, slicedMove)
        i, j = fullBoardMove
        
        # Apply the move directly to the full board copy
        myBoard[i][j] = player  # Simulate the move for the current player
        
        # Evaluate the full board after the move
        score = boardBalance(myBoard)
        
        # Undo the move by resetting it to 0 (empty)
        myBoard[i][j] = 0  # Undo the move
        
        # Store the move and its evaluation score
        move_scores.append((fullBoardMove, score))

    # Sort moves based on their score in descending order (best moves first)
    move_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Extract the ordered moves
    ordered_moves = [move for move, score in move_scores]
    
    return ordered_moves

class DragonWarriorAgent:

    def alphaBetaPruning(self, fullBoard, bufferBoard, evalMoves, depth, alpha, beta, maximizingPlayer, moveNumber, timeLimit, startTime, callNum=0):
        ''' Returns the best move for the given board and depth utilizing Alpha Beta Pruning.
        Respects the set timeLimit, and utilizes unoredered, yet strategically selected/sliced
        positions to evaluate, based on the moveNumber '''
        # time check
        if time.time() - startTime > timeLimit:
            return None, None

        # I have checks previous to calling alphaBeta that prevent/execute wins
        # So when Call Number is 1, it does not need to check if there is a winner (that would have been previously detected)
        if callNum <= 1:
            if depth == 0:
                return boardBalance(bufferBoard), None

        else:
            if depth == 0:
                winner = checkWin(fullBoard)
                if winner == 1:
                    return float('inf'), None
                elif winner == -1:
                    return float('-inf'), None
                else:
                    return boardBalance(bufferBoard), None

            if depth != 0:
                winner = checkWin(fullBoard)
                if winner == 1:
                    return float('inf'), None  # Win for maximizing player
                elif winner == -1:
                    return float('-inf'), None  # Win for minimizing player
                elif boardComplete(fullBoard):
                    return 0, None


        bestMove = None

        # Le toca al maximizing player
        if maximizingPlayer:
            maxEval = float('-inf')
            for i, move in enumerate(evalMoves):
                # Check if the time limit has been exceeded within the loop
                if time.time() - startTime > timeLimit:
                    return None, None
                
                bufferedMove = boardMoveReducer(fullBoard, bufferBoard, move)

                fullBoard[move[0], move[1]] = 1
                bufferBoard[bufferedMove[0], bufferedMove[1]] = 1
                eval, _ = self.alphaBetaPruning(fullBoard, bufferBoard, evalMoves[:i] + evalMoves[i + 1:], depth - 1, alpha, beta, False, moveNumber + 1, timeLimit, startTime, callNum + 1)
                fullBoard[move[0], move[1]] = 0
                bufferBoard[bufferedMove[0], bufferedMove[1]] = 0

                if eval is None:
                    return None, None  # time check

                if eval > maxEval:
                    maxEval = eval
                    bestMove = move
                alpha = max(alpha, eval)
                
                if beta <= alpha:
                    break  # Prune em
            return maxEval, bestMove

        # le toca al otro (minimizing player)
        else:
            minEval = float('inf')
            for i, move in enumerate(evalMoves):

                # time check
                if time.time() - startTime > timeLimit:
                    return None, None

                bufferedMove = boardMoveReducer(fullBoard, bufferBoard, move)

                fullBoard[move[0], move[1]] = -1
                bufferBoard[bufferedMove[0], bufferedMove[1]] = -1
                eval, _ = self.alphaBetaPruning(fullBoard, bufferBoard, evalMoves[:i] + evalMoves[i + 1:], depth - 1, alpha, beta, True, moveNumber + 1, timeLimit, startTime, callNum + 1)
                fullBoard[move[0], move[1]] = 0
                bufferBoard[bufferedMove[0], bufferedMove[1]] = 0

                if eval is None:
                    return None, None # time check

                if eval < minEval:
                    minEval = eval
                    bestMove = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Prune em
            return minEval, bestMove

    def iterativeDeepeningAlphaBeta(self, fullBoard, bufferBoard, evalMoves, maxDepth, alpha, beta, maximizingPlayer, moveNumber, timeLimit):
        ''' Calls AlphaBeta Pruning function using iterative deepening '''
        startTime = time.time()
        bestMove = None
        depthReached = 0
        

        for depth in (1, 3, 4, 5, 6, 7, 8, 9, 10, maxDepth+1):
            # Call alpha-beta pruning with the current depth
            moveEval, move = self.alphaBetaPruning(fullBoard, bufferBoard, evalMoves, depth, alpha, beta, maximizingPlayer, moveNumber, timeLimit, startTime)
            
            # If alphaBetaPruning ran out of time, return the best move found so far
            if moveEval is None or time.time() - startTime >= timeLimit:
                break

            # Update the best move found at this depth
            bestMove = move
            bestEval = moveEval
            depthReached = depth
            
            # Optional: Reorder moves based on evaluations at this depth
            if moveEval is not None:
                evalMoves = sorted(evalMoves, key=lambda move: moveEval if move == bestMove else 0, reverse=maximizingPlayer)

        # print(f"Maximum depth reached: {depthReached}")
        return bestEval, bestMove  # Return the best move found within the time limit

    def action(self, board):
        t0 = time.time()

        rows, cols = board.shape
        ones = np.count_nonzero(board == 1)
        minus_ones = np.count_nonzero(board == -1)

        if self.moveNumber == 0:
            if minus_ones == 1:
                self.first_turn = 'opponent'
            elif minus_ones == 0:
                self.first_turn = 'me'

        self.info = boardInfo(board)

        # Forced Move (solo queda 1 lugar para poner)
        boardIsFull = self.info.boardFull(board)
        if boardIsFull:
            # print("ta lleno .-.")
            return np.random.choice(np.flatnonzero(board == 0))
        
        # # print(f"Current Board Balance before I move is {boardBalance(board)}")

        # Ganar :)
        myWin = self.winningMove.winMove(board, player=1)
        if myWin is not None:
            # print("To my D.W. My star, my perfect silence")
            return myWin

        # Bloquear victoria enemiga inmediata 
        enemyWin = self.winningMove.winMove(board, player=-1)
        if enemyWin is not None:
            # # print("Enemy Winnable!")
            return enemyWin
        

        # lastHope = lastHopeScenario(board)
        # if lastHope:
        #     # print("LAST HOPE SCENARIO")
        #     drowningMove = lastHopeMove(board)
        #     if drowningMove is not None:
        #         return drowningMove

        # AlphaBeta Pruning
        slicedB = boardSlicer(board, self.moveNumber)
        bufferB = boardSlicer(board, self.moveNumber + 5, buffer=3)
        rows, cols = board.shape
        srows, scols = slicedB.shape

        mySlicedBoard = np.copy(slicedB)
        mySlicedBufferBoard = np.copy(bufferB)
        boardCopy = np.copy(board)

        evMoves = evaluableMoves(mySlicedBoard)
        nonEvMoves = uneavaluableMoves(mySlicedBoard)
        extraMoves = genBorderMoves(board, mySlicedBoard, nonEvMoves=nonEvMoves)
        # print(f"Extra Evaluable Moves are: {extraMoves}")

        myBoardCopy = np.copy(board)
        ordMoves = orderMoves(myBoardCopy, mySlicedBoard, evMoves, extraMoves, player=1)
        # print(f"Ordered Moves to evaluate are {ordMoves}")

        # print(f"\nDragon move number: {self.moveNumber}, Dragon branching: {len(ordMoves)}")
        
        t1Executing = time.time() - t0
        moveEval, abMove = self.iterativeDeepeningAlphaBeta(
            boardCopy,               # Full board
            mySlicedBufferBoard,       # Buffer board
            ordMoves,                  # Ordered moves
            maxDepth=50,               # Max depth for iterative deepening
            alpha=float('-inf'),       # Alpha
            beta=float('inf'),         # Beta
            maximizingPlayer=True,     # Whether it's the maximizing player's turn
            moveNumber=self.moveNumber, # Current move number
            timeLimit=4.75 - t1Executing # Time limit in seconds
        )


        if abMove is not None:
            # print(f"Move Chosen by AB was {abMove} with an evaluation of {moveEval}")
            print(f"Time Dragon took with AlphaBeta: {time.time() - t0}")
            self.moveNumber += 1
            return boardCoordinator(board, abMove)
        else:
            self.abortedTimes += 1
            # print(f"Dragon had to abort AlphaBeta, that's {self.abortedTimes} times now")

        connectedMove = self.strat.connectStrat(board)

        if connectedMove is not None:
            daMove = connectedMove
        # uncomment to playom.choice(np.flatnonzero(board == 0))
        
        self.moveNumber += 1
        print(f"Final Time taken Dragon: {time.time() - t0} \n")
        return daMove
        
