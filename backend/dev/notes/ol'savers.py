''' Ol' savers just that might actually be useful! (for testing which is better mainly, cause they aren't 100% proven yet)'''

class saver:
    # name is self-explanatory
    def alphaBetaModelWithoutIterativeDeepening(self, board, board_to_play, depth, alpha, beta, maximizingPlayer):
        """ Applies Alpha Beta Pruning techniques to Minimax to explore the game tree and find the best move to play in advanced depth"

        Args:
            board (np.ndarray): Current state of the board, in a 4d numpy array of dimension 3x3x3x3

            board_to_play (tuple or None): Tuple (a, b) indicating the global_board coordinates of the subboard to play in
                                            If None then can choose any board

            moves (tuple): List of moves to play (generated dynamically in the function for recursive calls)
            depth (int): Level of Recursion reached

            alpha (float): Alpha value for pruning (initially -infinity), representing the best value for the maximizing player.
            beta (float): Beta value for pruning (initially +infinity), representing the best value for the minimizing player.

            maximizingPlayer (bool): True for the agent, False for the rival

        Returns:
            float: The best value for the maximizing player
        """

        # if depth == self.depth:
        #     print(f"Monke! My depth equality check does work")

        # Base case: If we've reached the maximum depth or the game state is terminal (win/loss/draw)
        winner = checkBoardWinner(board)
        if winner != 0:
            return winner * 100000, None
        else:
            if depth == 0:
                return self.boardBalance(board), None
            # if boars isOver, but winner == 0, then it must be full, thus balance=0
            elif ((self.countPlayableBoards(board) == 0) or (isFull(board))):
                print(f"Monkey found over board (drawn) in recursion!")
                return 0, None
        # Si winner == 0, board is not over, and depth != 0, then we keep going

        best_move = None

        # Generate moves based on the current state
        if board_to_play is not None:
            row, col = board_to_play
            local_to_play = board[row, col]
            local_moves = np.argwhere(local_to_play == 0)
            if local_moves.size == 0:
                    raise ValueError(f"Local Moves was Empty! Conditions were: maxi={maximizingPlayer}, depth={depth}, a={alpha}, b={beta}. The local board was {(row, col)} and looked like: {local_to_play}\n Current global board was:\n {board} ")
            if depth == self.depth:
                print(f"Monkey AB Depth Initia, btp is not None, board to play is: {board_to_play}")
                print(f"Monkey AB Depth Initia, btp is not None, moves to consider are: {local_moves}")

            if maximizingPlayer:
                max_eval = float('-inf')
                for move in local_moves:
                    loc_row, loc_col = move

                    board[row, col][loc_row, loc_col] = 1 # Simulate my move
                    new_board_to_play = None if self.get_over_hash(board[loc_row, loc_col]) else (loc_row, loc_col)
                    eval, _ = self.alphaBetaModel(board, new_board_to_play, depth - 1, alpha, beta, False)
                    board[row, col][loc_row, loc_col] = 0 # Undo my move

                    if eval > max_eval:
                        max_eval = eval
                        best_move = move
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break  # Beta cutoff

                if best_move is None:
                    raise ValueError(f"Move was None! Conditions were: maxi={maximizingPlayer}, depth={depth}, a={alpha}, b={beta}, max_eval was {max_eval}. \nThe local board was {(row, col)} and it looked like\n: {local_to_play}. \nIts local moves were\n {local_moves}\n Current global board was:\n {board} ")
                final_best_move = [row, col, best_move[0], best_move[1]]
                return max_eval, final_best_move
            
            else:
                # Minimizer
                min_eval = float('inf')
                for move in local_moves:
                    loc_row, loc_col = move

                    board[row, col][loc_row, loc_col] = -1 # Simulate rival move
                    new_board_to_play = None if self.get_over_hash(board[loc_row, loc_col]) else (loc_row, loc_col)
                    eval, _ = self.alphaBetaModel(board, new_board_to_play, depth - 1, alpha, beta, True)
                    board[row, col][loc_row, loc_col] = 0 # Undo rival move
                    
                    if eval < min_eval:
                        min_eval = eval
                        best_move = move
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break  # Alpha cutoff

                if best_move is None:
                    raise ValueError(f"Move was None! Conditions were: maxi={maximizingPlayer}, depth={depth}, a={alpha}, b={beta}, min_eval was {min_eval}. \nThe local board was {(row, col)} and it looked like\n: {local_to_play}. \nIts local moves were\n {local_moves}\n Current global board was:\n {board} ")
                final_best_move = [row, col, best_move[0], best_move[1]]
                return min_eval, final_best_move

        else:
            global_moves = []
            der_playable_boards = self.genPlayableBoards(board)
            # if depth == self.depth:
            #     print(f"Monkey AB Depth Initia, btp is None, boards to play are: {der_playable_boards}")
            for (row, col) in der_playable_boards:
                local_board = board[row, col]
                empty_indices = np.argwhere(local_board == 0)
                
                for submove in empty_indices:
                    local_row, local_col = submove
                    global_moves.append([row, col, int(local_row), int(local_col)])

            if not global_moves:
                raise ValueError(f"Global moves are empty! Conditions were: maxi={maximizingPlayer}, depth={depth}, a={alpha}, b={beta}. The playble boards were {der_playable_boards}\n Current global board was:\n {board} ")

            # order the global moves
            # if depth == self.depth:
            #     print(f"Monkey AB Depth Initia, btp is None, moves to consider are: {global_moves}")            

            if maximizingPlayer:
                max_eval = float('-inf')
                for move in global_moves:
                    
                    if depth == self.depth:
                        if not self.isTrulyPlayable(board, move[0], move[1], move[2], move[3]):
                            raise ValueError(f"Monkey is at call number 0, considering invalid move: {move}")

                    row, col, loc_row, loc_col = move

                    board[row, col][loc_row, loc_col] = 1 # Simulate my move
                    new_board_to_play = None if self.get_over_hash(board[loc_row, loc_col]) else (loc_row, loc_col)
                    eval, _ = self.alphaBetaModel(board, new_board_to_play, depth - 1, alpha, beta, False)
                    board[row, col][loc_row, loc_col] = 0 # Undo my move

                    if eval > max_eval:
                        max_eval = eval
                        best_move = move
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
                # if best_move is None:
                #     raise ValueError(f"Move was None! Conditions were: maxi={maximizingPlayer}, depth={depth}, a={alpha}, b={beta}")
                return max_eval, best_move
            
            else:
                # Minimizer
                min_eval = float('inf')
                for move in global_moves:

                    if depth == self.depth:
                        if not self.isTrulyPlayable(board, move[0], move[1], move[2], move[3]):
                            raise ValueError(f"Monkey is at call number 0, considering invalid move: {move}")

                    row, col, loc_row, loc_col = move

                    board[row, col][loc_row, loc_col] = -1 # Simulate rival move
                    new_board_to_play = None if self.get_over_hash(board[loc_row, loc_col]) else (loc_row, loc_col)
                    eval, _ = self.alphaBetaModel(board, new_board_to_play, depth - 1, alpha, beta, True)
                    board[row, col][loc_row, loc_col] = 0 # Undo rival move

                    if eval < min_eval:
                        min_eval = eval
                        best_move = move
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
                # if best_move is None:
                    # raise ValueError(f"Move was None! Conditions were: maxi={maximizingPlayer}, depth={depth}, a={alpha}, b={beta}")
                return min_eval, best_move
