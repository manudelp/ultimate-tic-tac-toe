import numpy as np
import math
import time
import random
import ast
import os
from colorama import Style, Fore
from typing import List, Tuple, Dict, Any, Union, Optional

# Other Playing Info
"""
Strategy: Random (for now)
"""

# Heuristic Info
'''
# HEURISTIC

# # Local Board Evaluation
1 element in Line = ± 0.2
2 elements in Line = ± 0.6
Local Board Eval = sum(All 8 Line Evals, 3 Rows, 3 Cols, 2 Diags)
Board is Won = ± 10

# # Board Balance
Board Balance = Weighted Sum of All 9 Local Board Evals
If Local Board is Center, Multiply by 1.5
If Local Board is Corner, Multiply by 1.25
If Local Board is Edge, Do Not Multiply

'''

# El GOAT
class FooFinderAgent:
    # Gameplay Essentials 🎯📍 (⚠️ WARNING: DO NOT EDIT FUNCTION NAMES NOR ARGUMENTS ⚠️)
    def __init__(self):
        self.id = -1
        self.name = "Foo Finder"
        self.icon = "👑"
        self.description = "The best agent in the world, the one and only Foo Finder. He is the best agent in the world, and he knows it. Tiembla Arkadiusz"
        self.difficulty = 5
        self.loaded_up = False
        
        # Temporary to not break
        self.load()

    def __str__(self):
        self.str = f"{self.name}{self.icon}"
        return self.str

    def load(self):
        ''' Loads all the class elements and hashes for the agent to be ready for a game or set of games 
        To be called at most at the start of every game, ideally at the start of every set of games so as to not waste much time '''

        print(Style.BRIGHT + Fore.LIGHTBLUE_EX + f"Loading {self.name}..." + Style.RESET_ALL)
        # Game Track
        self.moveNumber = 0
        self.foo_pieces = 0
        self.rival_pieces = 0
        self.empty_pieces = 0
        
        # Class Sets
        self.over_boards_set = set()
        self.model_over_boards_set = set()
        self.playable_boards_set = set()
        self.model_playable_boards_set = set()
        
        # Board Info
        self.wonBoards = {}
        self.modelWonBoards = {}
        self.global_board_results = np.zeros((3, 3), dtype=int)
        self.model_global_board_results = np.zeros((3, 3), dtype=int)
        self.board_array = None
        self.board_tuple = None
        
        # Minimax Info
        self.time_limit = 8 # Seconds
        self.MIDGAME_MOVES = 15
        self.ENDGAME_EMPTIES = 3 #TODO: Adjust Endgame Empties Value!
        self.total_minimax_time = 0
        self.minimax_plays = 0
        
        # Hash Up
        self.hash_loading()
        
        # Register Load
        self.loaded_up = True

    def reset(self):
        # if self.minimax_plays == 0:
            # raise ValueError(Style.BRIGHT + Fore.RED + "Reset has been called, it's not the first game but minimax_plays is 0..." + Style.RESET_ALL)
        
        print("FooFinder Reset Lets Goo! 🚀")
        # Counts
        self.moveNumber = 0
        self.foo_pieces = 0
        self.rival_pieces = 0
        self.empty_pieces = 0
        
        # Sets
        self.over_boards_set = set()
        self.model_over_boards_set = set()
        self.playable_boards_set = set()
        self.model_playable_boards_set = set()
        
        # Board Info
        self.wonBoards = {}
        self.modelWonBoards = {}
        self.global_board_results = np.zeros((3, 3), dtype=int)
        self.board_array = None
        self.board_tuple = None

        # Minimax Info
        # average_minimax_time = self.total_minimax_time / self.minimax_plays
        # print(Style.BRIGHT + Fore.MAGENTA + f"\n{self.name} played Minimax {self.minimax_plays} times with an average time of {average_minimax_time:.4f} seconds" + Style.RESET_ALL)
        self.total_minimax_time = 0
        self.minimax_plays = 0

    def action(self, board: np.array, board_to_play: Union[Tuple[int, int], None] = None):
        '''
        Gets called in the game to determine the Agent Action
        All calls of agent functions & utilities get called by the server through this function
        Returns the move that the Agent choses to play next, given the current state of the game it has to play in

        Args:
            board (np.ndarray): Current state of the board, comprised of a 3x3 grid of 3x3 local tic tac toe boards, as a 4D Numpy Array (3x3x3x3)

            board_to_play (Union[Tuple[int, int], None]): None if the next board to play can be arbitrarily chosen, otherwise a tuple with the 2d global coordinates of the local board to play in
            Defaults to None (if any local board can be chosen).

        Returns:
            best_move (tuple): The move to play with its 4 coordinates in order (global_row, global_col, local_row, local_col)
        '''

        # Time Start
        self.start_time = time.time()
        print(f"{self.name} action begins, move number is {self.moveNumber}")

        # Smart-Board Transformations
        self.board_array = self.board.copy()
        self.board_tuple = boardToTuple(board)
        self.board_bytes = boardToHash(board)

        # Board Info Class Elements
        self.updateWonBoards(board)
        self.updateGlobalResults(board)
        self.updatePlayableBoards(board)
        
        self.modelWonBoards = self.wonBoards.copy()
        self.model_global_board_results = self.global_board_results.copy()
        self.model_over_boards_set = self.over_boards_set.copy()
        self.model_playable_boards_set = self.playable_boards_set.copy()

        self.foo_pieces = self.countPlayerPieces(board, player=1)
        self.rival_pieces = self.countPlayerPieces(board, player=-1)
        self.empty_pieces = self.countPlayerPieces(board, player=0)
        self.playable_pieces = self.countPlayablePieces(board)

        # Pre-Index Local Boards
        self.local_b00 = board[0, 0]
        self.local_b01 = board[0, 1]
        self.local_b02 = board[0, 2]
        self.local_b10 = board[1, 0]
        self.local_b11 = board[1, 1]
        self.local_b12 = board[1, 2]
        self.local_b20 = board[2, 0]
        self.local_b21 = board[2, 1]
        self.local_b22 = board[2, 2]

        # Ensure it's 3x3
        self.shape_rows, self.shape_cols, self.shape_subrows, self.shape_subcols = board.shape
        if self.shape_rows != 3 or self.shape_cols != 3 or self.shape_subrows != 3 or self.shape_subcols != 3:
            raise ValueError("Invalid Board Shape: El tablero no esta siendo un 3x3x3x3")

        # If No One has Played, We Play Center-Center (avoids self.moveNumber check)
        if np.count_nonzero(board) == 0:
            if self.moveNumber != 0:
                raise ValueError(f"FooFinder, No one has played, but move number is not 0, move number is {self.moveNumber}")
            if board[1, 1][1, 1] != 0:
                raise ValueError("FooFinder, No one has played, but center-center is not empty")
            self.moveNumber += 1
            return 1, 1, 1, 1

        # Aca iria si implementas un buen global board hashing con get_boardMove or something
        # en el cual ves si tu alguna de tus posibles moves esta en el respectivo hash!
        # consider que el hash tiene archivos para cada board_to_play

        # Ahora si! El Gameplay
        if board_to_play is None:

            # Immediate Win Check
            immediate_win = self.immediateWinMove(board)
            if immediate_win is not None:
                print("Andamo' Kung-Fu Fighting!")
                return immediate_win

            # Early Game
            if self.moveNumber < self.MIDGAME_MOVES:
                #TODO Early Game
                pass

            # Mid Game
            if self.moveNumber >= self.MIDGAME_MOVES and self.playable_pieces < self.ENDGAME_EMPTIES:
                #TODO Mid Game
                pass

            # Late Game
            if self.playable_pieces <= self.ENDGAME_EMPTIES:
                #TODO Late Game
                pass

            # TODO: Replace this with actual minimax and insert it into every scenario 
            # with the respective function (early game, mid game, late game)
            minimax_move = None
            # TODO FOOFINDER CHANGE ITERDEEP PARAMETERS WHEN BTP IS NONE, LOWER DEPTH!!
            if minimax_move is None:
                raise ValueError("Minimax Failed to Find a Move! Board to play was None")
            
            global_row, global_col, local_row, local_col = minimax_move
            self.moveNumber += 1
            return global_row, global_col, local_row, local_col


        # BOARD TO PLAY IS NOT NONE!
        else:   
            global_row, global_col = board_to_play 
            subboard = board[global_row, global_col]

        # Immediate Win Check
        immediate_win = self.immediateWinMove(board)
        if immediate_win is not None:
            print("Andamo' Kung-Fu Fighting!")
            return immediate_win

        # Early Game
        if self.moveNumber < self.MIDGAME_MOVES:
            #TODO Early Game
            pass

        # Mid Game
        if self.moveNumber >= self.MIDGAME_MOVES and self.playable_pieces < self.ENDGAME_EMPTIES:
            #TODO Mid Game
            pass

        # Late Game
        if self.playable_pieces <= self.ENDGAME_EMPTIES:
            #TODO Late Game
            pass

        # TODO: Replace this with actual minimax and insert it into every scenario 
        # with the respective function (early game, mid game, late game)
        minimax_move = None
        # TODO: FOOFINDER CHANGE ITERDEEP PARAMETERS WHEN BTP!=NONE, HIGHER DEPTH!!
        if minimax_move is None:
            raise ValueError(f"Minimax Failed to Find a Move! Board to play was {board_to_play}")

    def hash_loading(self):
        self.hash_winning_boards = {}
        self.hash_eval_boards = {}
        self.hash_eval_v2_boards = {}
        self.hash_eval_v3_boards = {}
        self.hash_boards_information = {}
        self.hash_results_boards = {}
        self.hash_draw_boards = {}
        self.hash_over_boards = {}
        self.hash_winnable_boards_by_one = {}
        self.hash_winnable_boards_by_minus_one = {}
        self.hash_HyphenNumeric_boards = {}
        self.hash_HyphenNumeric_boards_rival = {}
        self.hash_winning_results_boards = {}
        self.hash_draw_results_boards = {}

        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # Construct the absolute paths to the files
        winning_boards_path = os.path.join(root_dir, 'agents', 'hashes', 'hash_winning_boards.txt')
        draw_boards_path = os.path.join(root_dir, 'agents', 'hashes', 'hash_draw_boards.txt')
        over_boards_path = os.path.join(root_dir, 'agents', 'hashes', 'hash_over_boards.txt')
        evaluated_boards_path = os.path.join(root_dir, 'agents', 'hashes', 'hash_evaluated_boards.txt')
        board_info_path = os.path.join(root_dir, 'agents', 'hashes', 'hash_boards_information.txt')
        results_eval_path = os.path.join(root_dir, 'agents', 'hashes', 'hash_results_board_eval.txt')
        winning_results_path = os.path.join(root_dir, 'agents', 'hashes', 'hash_winning_results_boards.txt')
        draw_results_path = os.path.join(root_dir, 'agents', 'hashes', 'hash_draw_results_boards.txt')
        winnable_boards_one_path = os.path.join(root_dir, 'agents', 'hashes', 'hash_winnable_boards_by_one.txt')
        winnable_boards_minus_one_path = os.path.join(root_dir, 'agents', 'hashes', 'hash_winnable_boards_by_minus_one.txt')

        # Load the boards using the absolute paths
        self.load_winning_boards(winning_boards_path)
        self.load_drawn_boards(draw_boards_path)
        self.load_over_boards(over_boards_path)
        self.load_evaluated_boards(evaluated_boards_path)
        # self.load_boards_info(board_info_path)
        # self.load_results_board_eval(results_eval_path)
        # self.load_winning_results_boards(winning_results_path)
        # self.load_draw_results_boards(draw_results_path)
        self.load_winnable_boards_one(winnable_boards_one_path)
        self.load_winnable_boards_minus_one(winnable_boards_minus_one_path)

    # GAYMING LOGIC BELOW

    # Minimax General Auxiliaries 🌲🧠
    # TODO REPLACE ME CON LAS DE MONKEY Y JARDITOBETTER Y TODAS LAS MEJORES
    def new_parameters(self, board, row, col, loc_row, loc_col):
        # TIMEIT APPROVED ✅
        ''' Simulates a move on the board, given the 4d move and the player
        Returns the new_board_to_play and the new_moves_to_try '''
        if self.get_over_hash(board[loc_row, loc_col]):
            return None, self.generate_global_moves(board)
        else:
            return (loc_row, loc_col), np.argwhere(board[loc_row, loc_col] == 0)
        
        # Unfreeze in case it breaks! (this below would be kind of TIMEIT ACCEPTED ☑️)
        # if self.get_over_hash(board[loc_row, loc_col]):
        #     board_to_play = None
        #     moves_to_try = self.generate_global_moves(board)
        # else:
        #     board_to_play = (loc_row, loc_col)
        #     moves_to_try = np.argwhere(board[loc_row, loc_col] == 0)
        # return board_to_play, moves_to_try

    def generate_local_moves(self, board) -> List[np.array]:
        # TIMEIT ACCEPTED ☑️ (Solo se usa por fuera del Minimax, asi que aceptable, plus testing revealed it's time-great!)
        ''' Given a local board, generates a list of all playable moves '''
        local_moves = np.argwhere(board == 0)
        
        # Turn 2D Array into List of Arrays
        list_moves = [local_moves[i] for i in range(len(local_moves))]

        return list_moves

    def generate_global_moves(self, board):
        # TIMEIT APPROVED ✅
        ''' Given a global board, generates a list of all playable moves 
        in the playable local boards '''
        global_moves = []
        for (row, col) in self.genPlayableBoards(board):
            for submove in np.argwhere(board[row, col] == 0):
                global_moves.append(np.array([row, col, submove[0], submove[1]]))
        return global_moves

    def TODO_MINIMAX(self):
        ''' Lists some other TODOs for the Minimax '''
        
        # TODO Ver cual tecnica de llamado de llamar *AlphaBeta* es mas eficiente: La de jardy.py, la de twinny.py, o la de ordy.py
        
        None

    def alphaBetaModel(self, board, board_to_play, depth, alpha, beta, maximizingPlayer):
        # TODO: This is a draft
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

        # Base case: If we've reached the maximum depth or the game state is terminal (win/loss/draw)
        winner = self.get_isWon(self.model_global_board_results)
        if winner != 0:
            return winner * 100000, None
        else:
            if depth == 0:
                return self.boardBalance(board), None
            # if boars isOver, but winner == 0, then it must be full, thus balance=0

            # TODO: Chequeo de global board terminal!
            # pensa que va a equivocarse cuando hay muchos local_boards que son empates, los toma como 0s abiertos
            # fijate cuando hagas el hash global, de poder chequear cuantos local_boards playables hay o algo asi
            # y si hay 0 pero no hay winner, then it's over, it's a draw! 
            # por ahora la que tiene MonkeyAgent con self.countPlaable Boards cumple la funcion que deberia
            # pero no es Time Optimal maybe, aunque maybe that doesnt even matter tbh
            elif ((self.get_over_hash(self.model_global_board_results)) or (isFullGlobal(board))):
                # Need to check both cause si esta lleno pero ninguno gano ponele, los results son todos 0, y thats not over
                return 0, None
        # Si winner == 0, board is not over, and depth != 0, then we keep going

        best_move = None

        # Generate moves based on the current state
        if board_to_play is not None:
            row, col = board_to_play
            local_to_play = board[row, col]
            local_moves = np.argwhere(local_to_play == 0)

            if maximizingPlayer:
                max_eval = float('-inf')
                for move in local_moves:
                    loc_row, loc_col = move
                    local_board = board[row, col]

                    # Simulate my move, update the global board results
                    local_board[loc_row, loc_col] = 1
                    local_won = self.get_isWon(local_board)
                    if local_won != 0:
                        self.model_global_board_results[row, col] = local_won
                    new_board_to_play = None if self.get_over_hash(board[loc_row, loc_col]) else (loc_row, loc_col)
                    eval, _ = self.alphaBetaModel(board, new_board_to_play, depth - 1, alpha, beta, False)
                    # Undo my move, reset the global board results
                    local_board[loc_row, loc_col] = 0 
                    if local_won != 0:
                        self.model_global_board_results[row, col] = 0

                    if eval > max_eval:
                        max_eval = eval
                        best_move = move
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break  # Beta cutoff
                return max_eval, best_move
            
            else:
                # Minimizer
                min_eval = float('inf')
                for move in local_moves:
                    loc_row, loc_col = move
                    local_board = board[row, col]

                    # Simulate opponent move, update the global board results
                    local_board[loc_row, loc_col] = -1
                    local_won = self.get_isWon(local_board)
                    if local_won != 0:
                        self.model_global_board_results[row, col] = local_won
                    new_board_to_play = None if self.get_over_hash(board[loc_row, loc_col]) else (loc_row, loc_col)
                    eval, _ = self.alphaBetaModel(board, new_board_to_play, depth - 1, alpha, beta, True)
                    # Undo opponent move, reset the global board results
                    board[row, col][loc_row, loc_col] = 0 
                    if local_won != 0:
                        self.model_global_board_results[row, col] = 0
                    
                    if eval < min_eval:
                        min_eval = eval
                        best_move = move
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break  # Alpha cutoff
                return min_eval, best_move

        else:
            moves = self.gen_all_local_moves(board)
            
            if maximizingPlayer:
                max_eval = float('-inf')
                for move in moves:
                    row, col, loc_row, loc_col = move
                    local_board = board[row, col]

                    # Simulate my Move, update the global board results
                    local_board[loc_row, loc_col] = 1
                    local_won = self.get_isWon(local_board)
                    if local_won != 0:
                        self.model_global_board_results[row, col] = local_won
                    new_board_to_play = None if self.get_over_hash(board[loc_row, loc_col]) else (loc_row, loc_col)
                    eval, _ = self.alphaBetaModel(board, new_board_to_play, depth - 1, alpha, beta, False)
                    # Undo my move, reset the global board results
                    local_board[loc_row, loc_col] = 0
                    if local_won != 0:
                        self.model_global_board_results[row, col] = 0

                    if eval > max_eval:
                        max_eval = eval
                        best_move = move
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
                return max_eval, best_move
            
            else:
                # Minimizer
                min_eval = float('inf')
                for move in moves:
                    row, col, loc_row, loc_col = move
                    local_board = board[row, col]

                    # Simulate opponent Move, update the global board results
                    local_board[loc_row, loc_col] = -1
                    local_won = self.get_isWon(local_board)
                    if local_won != 0:
                        self.model_global_board_results[row, col] = local_won
                    new_board_to_play = None if self.get_over_hash(board[loc_row, loc_col]) else (loc_row, loc_col)
                    eval, _ = self.alphaBetaModel(board, new_board_to_play, depth - 1, alpha, beta, True)
                    # Undo opponent move, reset the global board results
                    local_board[loc_row, loc_col] = 0
                    if local_won != 0:
                        self.model_global_board_results[row, col] = 0

                    if eval < min_eval:
                        min_eval = eval
                        best_move = move
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
                return min_eval, best_move

    def iterativeDeepening(self):
        # TODO: Complete this function
        None

    def moveQuality(self, board, move: tuple) -> float:
        ''' Returns the quality of the given move by simulating the move and getting its boardBalance '''
        a, b, c, d = move
        board[a, b, c, d] = 1
        score = self.boardBalance(board)
        board[a, b, c, d] = 0
        return score

    def orderMoves(self, board, moves):
        ''' Given the array of possible moves to play, orders them in a way that the most promising moves are played first 
        Meaning, it orders them based on moveQuality in descending order (greatest quality first) '''
        # TODO: Order Moves
        None

    # Early Game Stage 🌄
    def alphaBetaEarlyGame(self):
        # TODO: Complete this function
        ''' Doesn't need to check if game is Over 
        Big one here... doesn't need to check Moves that lead to board_to_play is None 
        Make it only simulate moves that don't lead to board_to_play=None, for both players 
        So the moves that win a local board, even if they let board_to_play=None, will be used 
        
        The way to do this is to use the winnables board hash to check which moves not to expand
        So if a move leads to board_to_play = None, then check if that move is in the winnable boards hash
        This check is done by doing:
            if (loc_row, loc_col) in self.get_winnableMoves(local_board) -> bool
            if True, good, continue with logic
            else, dont evaluate that stinky ahh move
            
        If that's False, it's not worth expanding, just break the cycle, continue to the next move without
        calling the function recursively, to avoid checking moves that lead to btp=None which will advantage the rival.
        This only works at this early stage

        Another thing, if it's not already done strongly enough through the heuristic evaluation
        Then maybe add a particular emphasis (like a score bonus) to moves that lead to a local board win in this stage
        Especially if it's a move that doesn't lead to board_to_play=None for the enemy, 
        or that don't lead to the enemy going to a winnable board
        '''

        # if self.moveNumber + depth > 14:
        #     check winner 
        # else, don't check winner

        None

    def iterativeDeepeningEarlyGame(self):
        ''' 
        Call this while (depth + move_number) < 15 
        Already wrote this down for the alpha beta, but yeah
        If a move leads to board_to_play is None, only chose it if it's in the winnable boards hash of its local board
        Otherwise, continue to the next move without calling alpha beta on this one
        '''
        None

    def board_balance_earlygame(self, board):
        None

    # Mid Game Stage 🏞️
    def alphaBetaMidGame(self):
        # TODO: Complete this function
        ''' Checks everything cause it can be won or drawn at any point (for now... there might be some cooking
        done regarding the drawn part, although calculating when a global_board cannot be drawn in <=d moves might be
        more time costly than just simply hashing self.global_board_results in the draw_boards file to check '''
        return None
    
            # TODO: Aca proba si podes usar get_isWon(self.model_global_board_results) en vez de getGlobalWinner
            # fijate de actalizar bien el board mode_global__board_results
            # ya vimos que su tiempo es optimo! see timer_minimax.py for implementation and time test corroboration

        winner = self.get_isWon(self.model_global_board_results)
        if winner != 0:
            return winner * float('inf'), None
        else:
            if depth == 0:
                return self.boardBalance(board), None
            # if boars isOver, but winner == 0, then it must be full, thus balance=0
            elif self.get_over_hash(self.model_global_board_results):
                return 0, None
        # Si winner == 0, board is not over, and depth != 0, then we keep going

        # Logic
        ''' IMPORTANT! 
        Either with timeit or Profiler, time-test the following 3 options:
        - Not Ordering the Moves at all inside the Alpha Beta
        - Only Ordering the Moves inside the Alpha Beta if 
        '''

    def iterativeDeepeningMidGame(self):
        ''' Call this while 14 < (depth + move_number) < high '''
        None

    def board_balance_midgame(self, board):
        None

    # Late Game Stage 🌃
    def alphaBetaEndGame(self):
        # TODO: Complete this function
        ''' Doesn't need BoardBalance, just checks if Won or Draw
        Get inspiration from regular 3x3 Tic Tac Toe minimax which does exactly this! 
        Consider depth being the total amount of remaining empty pieces 

        Check at what depth=d you can run this function in less than 8 seconds, 
        and so start calling it when empty_pieces <= d

        And when/before it reaches depth=0, it will either return 1, -1 or 0 for value
        Which in this case, will mostly be 0 if it's a draw, by not finding in the winning_boards unless it wins on the last possible move.
        Just hash the self.model_global_board_results in draw_boards to check. 

        Implementation might be actually more different than it seems... might be worth checking out, or relating to-
        some 3x3 Tic Tac Toe Alpha Beta Pruning Code, since there it's always end game strategy of just checking for winner basically.
        
        ESTE CONCEPTO PODRIA IR PARA TODOS LOS ALPHABETAS, PERO BUENO ACA ES AUN MAS IMPORTANTE SI ES QUE ES UN BUEN CONCEPTO
        - Break / Exception / or smth
        for the alpha-beta pruning when a move is a winner?
        tipo, dont waste time doing more comparisons, just break everything and return it
        '''
        None

    def iterativeDeepeningLateGame(self):
        ''' Check at what depth=d you can run this function in less than 8 seconds, 
        and so start calling it when empty_playable_pieces <= d 
        Meaning empty pieces in playable boards
        
        Consider que si quedan por ejemplo, 16 empty_playable_pieces, entonces 
        quedan < 16 jugadas hasta un empate o victoria. Meaning que las iteraciones totales que quedan
        va a ser si o si menor a 16 factorial (16!), y chequear victoria es O(1)...'''
        None

    def board_balance_endgame(self, board):
        ''' In the case it does need some board balance... just make it the usual results stuff with the won boards connectivity through get_results_board_eval
        No need to waste time with Positional Scores, although to be fair no need to waste time with board balance at all either! '''
        None

    # Board Checks & Heuristic Auxiliaries 🧮✔️
    def boardBalance(self, board):
        # TODO: Yeah... actually make a good heuristic lmao
        # NEEDS TIME IMPROVEMENT 🚨
        # Don't use 'for' loops! Use direct indexing

        ''' 
        Returns the heuristic value of the board

        Currently Performs a Weighted Sum of All 9 Local Board Evals
        If Local Board is Center, Multiply by 1.5
        If Local Board is Corner, Multiply by 1.25
        If Local Board is Edge, Do Not Multiply
        '''
        balance = 0

        # TODO: Actually make it good, not just add up local balances

        # Auxiliar For Now!
        for r in range(3):
            for c in range(3):
                localBoard = board[r, c]

                # Weighted Sum
                if r == 1 and c == 1:
                    balance += 1.3 * localBoardEval(localBoard)
                elif (r == 0 or r == 2) and (c == 0 or c == 2):
                    balance += 1.1 * localBoardEval(localBoard)
                else:
                    balance += localBoardEval(localBoard)

                # balance += localBoardEval(localBoard)
        
        return balance

    def countPlayablePieces(self, board):
        ''' Counts how many playable pieces there are in total in the playable local boards of the global board '''
        # TODO! De mas esta decir, utilize the .get_playable_hash method for a model global results array

    def countPieces(self, board, player):
        # TIMEIT ACCEPTED ☑️ not relevant enough to be time-improved, it's just called once per action
        ''' Returns the amount of pieces from the given player, in the boards that are still Playable'''
        count = 0
        for row in range(3):
            for col in range(3):
                subboard = board[row, col]
                if self.get_playable_hash(subboard):
                    count += np.count_nonzero(subboard == player)
        return count

    def getGlobalWinner(self, board):
        # TIMEIT APPROVED ✅
        # TODO: THIS IS TEMPORARY!! REMOVE AND REPLACE WITH THE get_globalWinner function
        ''' Returns the winner of the global board, if any '''
        results = np.ndarray((3, 3), dtype=int)
        results[0, 0] = self.get_isWon(board[0, 0])
        results[0, 1] = self.get_isWon(board[0, 1])
        results[0, 2] = self.get_isWon(board[0, 2])
        results[1, 0] = self.get_isWon(board[1, 0])
        results[1, 1] = self.get_isWon(board[1, 1])
        results[1, 2] = self.get_isWon(board[1, 2])
        results[2, 0] = self.get_isWon(board[2, 0])
        results[2, 1] = self.get_isWon(board[2, 1])
        results[2, 2] = self.get_isWon(board[2, 2])

        return self.get_isWon(results)

    def determine_next_board(self, board, l_row, l_col):
        ''' Given the board and last 2 indices of a move, directing to a board 
        Returns the corresponding board_to_play (None if the board is won or full) '''
        return None if self.get_over_hash(board[l_row, l_col]) else (l_row, l_col)

    def isTrulyPlayable(self, board, move_row, move_col, move_row_local, move_col_local):
        # TIMEIT APPROVED ✅
        ''' Returns whether or not the move is truly playable, meaning if the space is empty and the board is playable '''
        local_board = board[move_row, move_col]
        return ((local_board[move_row_local, move_col_local] == 0) and (self.get_playable_hash(local_board)))

    # Class Element Auxiliaries 🎬📦
    def updateWonBoards(self, board):
        # TIMEIT ACCEPTED ☑️ not relevant enough to be time-improved, it's just called once per action
        ''' Updates the WonBoards class dictionary '''
        b00, b01, b10, b11, b20, b21, b02, b12, b22 = isWon(board[0, 0]), isWon(board[0, 1]), isWon(board[1, 0]), isWon(board[1, 1]), isWon(board[2, 0]), isWon(board[2, 1]), isWon(board[0, 2]), isWon(board[1, 2]), isWon(board[2, 2])
        
        if b00 != 0:
            self.wonBoards[(0, 0)] = b00
        if b01 != 0:
            self.wonBoards[(0, 1)] = b01
        if b02 != 0:
            self.wonBoards[(0, 2)] = b02
        if b10 != 0:
            self.wonBoards[(1, 0)] = b10
        if b11 != 0:
            self.wonBoards[(1, 1)] = b11
        if b12 != 0:
            self.wonBoards[(1, 2)] = b12
        if b20 != 0:
            self.wonBoards[(2, 0)] = b20
        if b21 != 0:
            self.wonBoards[(2, 1)] = b21
        if b22 != 0:
            self.wonBoards[(2, 2)] = b22

    def updateModelWonBoards(self, board):
        # TIMEIT APPROVED ✅
        ''' Updates the modelWonBoards class dictionary '''
        b00, b01, b10, b11, b20, b21, b02, b12, b22 = self.get_isWon(board[0, 0]), self.get_isWon(board[0, 1]), self.get_isWon(board[1, 0]), self.get_isWon(board[1, 1]), self.get_isWon(board[2, 0]), self.get_isWon(board[2, 1]), self.get_isWon(board[0, 2]), self.get_isWon(board[1, 2]), self.get_isWon(board[2, 2])

        if b00 != 0:
            self.modelWonBoards[(0, 0)] = b00
        if b01 != 0:
            self.modelWonBoards[(0, 1)] = b01
        if b02 != 0:
            self.modelWonBoards[(0, 2)] = b02
        if b10 != 0:
            self.modelWonBoards[(1, 0)] = b10
        if b11 != 0:
            self.modelWonBoards[(1, 1)] = b11
        if b12 != 0:
            self.modelWonBoards[(1, 2)] = b12
        if b20 != 0:
            self.modelWonBoards[(2, 0)] = b20
        if b21 != 0:
            self.modelWonBoards[(2, 1)] = b21
        if b22 != 0:
            self.modelWonBoards[(2, 2)] = b22

    def addWonBoard(self, board):
        # TIMEIT APPROVED ✅
        ''' Adds a won board directly to the won boards model dictionary '''
        self.modelWonBoards[board] = self.get_isWon(board)

    def updateOverBoards(self, board):
        # TIMEIT APPROVED ✅
        if self.get_over_hash(board[0, 0]):
            self.over_boards_set.add((0, 0))
        if self.get_over_hash(board[0, 1]):
            self.over_boards_set.add((0, 1))
        if self.get_over_hash(board[0, 2]):
            self.over_boards_set.add((0, 2))
        if self.get_over_hash(board[1, 0]):
            self.over_boards_set.add((1, 0))
        if self.get_over_hash(board[1, 1]):
            self.over_boards_set.add((1, 1))
        if self.get_over_hash(board[1, 2]):
            self.over_boards_set.add((1, 2))
        if self.get_over_hash(board[2, 0]):
            self.over_boards_set.add((2, 0))
        if self.get_over_hash(board[2, 1]):
            self.over_boards_set.add((2, 1))
        if self.get_over_hash(board[2, 2]):
            self.over_boards_set.add((2, 2))

    def updateModelOverBoards(self, board):
        # TIMEIT APPROVED ✅
        if self.get_over_hash(board[0, 0]):
            self.model_over_boards_set.add((0, 0))
        if self.get_over_hash(board[0, 1]):
            self.model_over_boards_set.add((0, 1))
        if self.get_over_hash(board[0, 2]):
            self.model_over_boards_set.add((0, 2))
        if self.get_over_hash(board[1, 0]):
            self.model_over_boards_set.add((1, 0))
        if self.get_over_hash(board[1, 1]):
            self.model_over_boards_set.add((1, 1))
        if self.get_over_hash(board[1, 2]):
            self.model_over_boards_set.add((1, 2))
        if self.get_over_hash(board[2, 0]):
            self.model_over_boards_set.add((2, 0))
        if self.get_over_hash(board[2, 1]):
            self.model_over_boards_set.add((2, 1))
        if self.get_over_hash(board[2, 2]):
            self.model_over_boards_set.add((2, 2))

    def updatePlayableBoards(self, board):
        # TIMEIT APPROVED ✅
        if self.get_playable_hash(board[0, 0]):
            self.playable_boards_set.add((0, 0))
        if self.get_playable_hash(board[0, 1]):
            self.playable_boards_set.add((0, 1))
        if self.get_playable_hash(board[0, 2]):
            self.playable_boards_set.add((0, 2))
        if self.get_playable_hash(board[1, 0]):
            self.playable_boards_set.add((1, 0))
        if self.get_playable_hash(board[1, 1]):
            self.playable_boards_set.add((1, 1))
        if self.get_playable_hash(board[1, 2]):
            self.playable_boards_set.add((1, 2))
        if self.get_playable_hash(board[2, 0]):
            self.playable_boards_set.add((2, 0))
        if self.get_playable_hash(board[2, 1]):
            self.playable_boards_set.add((2, 1))
        if self.get_playable_hash(board[2, 2]):
            self.playable_boards_set.add((2, 2))

    def updateModelPlayableBoards(self, board):
        # TIMEIT APPROVED ✅
        if self.get_playable_hash(board[0, 0]):
            self.model_playable_boards_set.add((0, 0))
        if self.get_playable_hash(board[0, 1]):
            self.model_playable_boards_set.add((0, 1))
        if self.get_playable_hash(board[0, 2]):
            self.model_playable_boards_set.add((0, 2))
        if self.get_playable_hash(board[1, 0]):
            self.model_playable_boards_set.add((1, 0))
        if self.get_playable_hash(board[1, 1]):
            self.model_playable_boards_set.add((1, 1))
        if self.get_playable_hash(board[1, 2]):
            self.model_playable_boards_set.add((1, 2))
        if self.get_playable_hash(board[2, 0]):
            self.model_playable_boards_set.add((2, 0))
        if self.get_playable_hash(board[2, 1]):
            self.model_playable_boards_set.add((2, 1))
        if self.get_playable_hash(board[2, 2]):
            self.model_playable_boards_set.add((2, 2))

    def updateGlobalResults(self, board):
        # TIMEIT ACCEPTED ☑️ not relevant enough to be time-improved, it's just called once per action
        ''' Updates the global_board_results class array to include 1s in the positions where player 1 has won,
        -1s where player -1 has won, and 0s where the board is not won. Positions are i*3 + j '''
        self.global_board_results[0, 0] = self.get_isWon(board[0, 0])
        self.global_board_results[0, 1] = self.get_isWon(board[0, 1])
        self.global_board_results[0, 2] = self.get_isWon(board[0, 2])
        self.global_board_results[1, 0] = self.get_isWon(board[1, 0])
        self.global_board_results[1, 1] = self.get_isWon(board[1, 1])
        self.global_board_results[1, 2] = self.get_isWon(board[1, 2])
        self.global_board_results[2, 0] = self.get_isWon(board[2, 0])
        self.global_board_results[2, 1] = self.get_isWon(board[2, 1])
        self.global_board_results[2, 2] = self.get_isWon(board[2, 2])

    def addGlobalResult(self, local_board, position):
        # TIMEIT APPROVED ✅
        ''' When a subboard is won, adds it to the global results '''
        self.model_global_board_results[position] = self.get_isWon(local_board)  

    def updateModelGlobalResults(self, board):
        # TIMEIT APPROVED ✅
        ''' Updates the model global results board '''
        self.model_global_board_results[0, 0], self.model_global_board_results[0, 1], self.model_global_board_results[0, 2] = self.get_isWon(board[0, 0]), self.get_isWon(board[0, 1]), self.get_isWon(board[0, 2])
        self.model_global_board_results[1, 0], self.model_global_board_results[1, 1], self.model_global_board_results[1, 2] = self.get_isWon(board[1, 0]), self.get_isWon(board[1, 1]), self.get_isWon(board[1, 2])
        self.model_global_board_results[2, 0], self.model_global_board_results[2, 1], self.model_global_board_results[2, 2] = self.get_isWon(board[2, 0]), self.get_isWon(board[2, 1]), self.get_isWon(board[2, 2])

    # Hashing Loading Auxiliaries 🔑📖
    def load_winning_boards(self, file_path):
        # TIMEIT ACCEPTED ☑️ (not relevant enough to be time-improved, it's just called once in the __init__)
        
        """
        Load the winning boards from a file and store them in a dictionary.
        Each board's state is stored as a key (using its byte representation) with the winner (1 or -1) as its value.
        """
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, winner = line.strip().split(':')
                    self.hash_winning_boards[bytes.fromhex(board_hex)] = int(winner)
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Winning boards will not be loaded.")

    def load_evaluated_boards(self, file_path):
        # TIMEIT ACCEPTED ☑️ (not relevant enough to be time-improved, it's just called once in the __init__)
        
        """
        Load the evaluated boards from a file and store them in a dictionary.
        Each board's state is stored as a key (using its byte representation) with its heuristic value.
        """
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, board_info_str = line.strip().split(':')
                    board_info_tuple = ast.literal_eval(board_info_str)
                    heuristic_value, result = board_info_tuple
                    self.hash_eval_boards[bytes.fromhex(board_hex)] = (float(heuristic_value), int(result))
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Evaluated boards will not be loaded.")

    def load_boards_info(self, file_path):
        ''' Load the evaluated boards from a file and store them in a dictionary '''
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, board_info_str = line.strip().split(':')
                    board_info_tuple = ast.literal_eval(board_info_str)
                    heuristic_value, result, positional_lead, positional_score = board_info_tuple
                    self.hash_boards_information[bytes.fromhex(board_hex)] = (float(heuristic_value), int(result), int(positional_lead), float(positional_score))
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Evaluated boards will not be loaded.")

    def load_drawn_boards(self, file_path):
        # TIMEIT ACCEPTED ☑️ (not relevant enough to be time-improved, it's just called once in the __init__)
        
        """
        Load the drawn boards from a file and store them in a dictionary.
        Each board's state is stored as a key (using its byte representation) with a boolean value.
        """
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, is_draw = line.strip().split(':')
                    self.hash_draw_boards[bytes.fromhex(board_hex)] = (is_draw == 'True')
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Drawn boards will not be loaded.")

    def load_move_boards(self, file_path):
        # TIMEIT ACCEPTED ☑️ (not relevant enough to be time-improved, it's just called once in the __init__)
        None

    def load_over_boards(self, file_path):
        # TIMEIT ACCEPTED ☑️ (not relevant enough to be time-improved, it's just called once in the __init__)
        ''' Loads the over boards from a file and stores them in a dictionary 
        Each board's state is stored as a key (using its byte representation)
        '''
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex = line.strip()
                    self.hash_over_boards[bytes.fromhex(board_hex)] = True
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Over boards will not be loaded.")        

    def load_winnable_boards_one(self, file_path):
        ''' 
        Loads the winnable boards from a file and stores them in a dictionary. 
        Each board's state is stored as a key (using its byte representation).
        They are stored as board : winning_moves,
        where winning_moves is a set of tuples with the moves to win.
        '''
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, moves = line.strip().split(':')
                    moves = ast.literal_eval(moves)  # Safely evaluate the set of tuples
                    self.hash_winnable_boards_by_one[bytes.fromhex(board_hex)] = set(moves)
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Winnable boards will not be loaded.")

    def load_winnable_boards_minus_one(self, file_path):
        ''' 
        Loads the winnable boards from a file and stores them in a dictionary. 
        Each board's state is stored as a key (using its byte representation).
        They are stored as board : winning_moves,
        where winning_moves is a set of tuples with the moves to win.
        '''
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, moves = line.strip().split(':')
                    moves = ast.literal_eval(moves)  # Safely evaluate the set of tuples
                    self.hash_winnable_boards_by_minus_one[bytes.fromhex(board_hex)] = set(moves)
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Winnable boards will not be loaded.")

    # Hashing Retrieval Auxiliaries 📚🔍
    def get_isWon(self, board):
        # TIMEIT APPROVED ✅
        """
        Retrieve the winner of a board from the preloaded dictionary of winning boards.
        Returns 1 if player 1 won, -1 if player -1 won, or None if there is no winner.
        """
        board_key = board.tobytes()
        return self.hash_winning_boards.get(board_key, 0)

    def get_eval(self, board):
        # TIMEIT APPROVED ✅
        """
        Retrieve the heuristic value of a board from the preloaded dictionary of evaluated boards.
        If the board is not in the dictionary, return None (or handle it as needed).
        """
        board_key = board.tobytes()
        local_eval, _ = self.hash_eval_boards.get(board_key, None)
        if local_eval is None:
            raise ValueError(f"Board {board} not found in evaluated boards.")
        return local_eval
    
    def get_isDraw(self, board):
        # TIMEIT APPROVED ✅
        """
        Retrieve the draw status of a board from the preloaded dictionary of drawn boards.
        Returns True if the board is a draw, False otherwise.
        """
        board_key = board.tobytes()
        return self.hash_draw_boards.get(board_key, False)

    def get_bestMove(self, board):
        '''
        go to generate_hashes.py
         Fijate si podes somehow hashear muchos tableros de super tic tac toe, pensa que hay maybe factores:
        - El tablero es un np.zeros, solo tenes que agregarle 2^81 (1s & -1s)
        - El tablero si o si tiene o la misma cantidad de 1s y -1s, o 1 mas de 1s que de -1s 
        '''
        None
    
    def get_over_hash(self, board):
        # TIMEIT APPROVED ✅
        ''' If the board is found in the over boards, return True, else False '''
        board_key = board.tobytes()
        return self.hash_over_boards.get(board_key, False)

    def get_playable_hash(self, board):
        # TIMEIT UNSURE 🤔 (yes it would be faster to just call not get_over_hash directly 
        # instead of calling get_playable_hash to call it as a mediator, dont know if its relevant enough to check tho)
        ''' Returns True if the board is playable, False otherwise '''
        return not self.get_over_hash(board)

    def get_winnableByOne(self, board):
        ''' Returns the set of winning moves for player 1, if the board is winnable '''
        board_key = board.tobytes()
        return self.hash_winnable_boards_by_one.get(board_key, set())

    def get_winnableByMinusOne(self, board):
        ''' Returns the set of winning moves for player -1, if the board is winnable '''
        board_key = board.tobytes()
        return self.hash_winnable_boards_by_minus_one.get(board_key, set())

    # Other Auxiliaries 🎲
    def randomMove(self, board):
        # TIMEIT ACCEPTED ☑️ (not relevant enough to be time-improved, it's just called once per action)
        empty_cells = np.flatnonzero(board == 0)

        # Randomly choose an empty cell from the available ones
        chosen_index = random.choice(empty_cells)
        local_row, local_col = np.unravel_index(chosen_index, board.shape)

        return local_row, local_col


# Auxiliary Functions
# Basic
def canPlay(board, x, y):
    # TIMEIT APPROVED ✅ 
    # Not much to test
    ''' Returns True if the (x, y) move in subboard can be played, False otherwise '''
    return board[x, y] == 0

def isFullGlobal(board):
    # TIMEIT APPROVED ✅
    # count_nonzero proven to be faster with timeit
    ''' Returns True if the board is full, False otherwise, works only for 9x9 global boards '''
    return (np.count_nonzero(board) == 81)

def notFullGlobal(board):
    # TIMEIT APPROVED ✅
    # count_nonzero proven to be faster with timeit
    ''' Returns True if the board is not full, False otherwise, works only for 9x9 global boards '''
    return (np.count_nonzero(board) != 81)

def isFullLocal(board):
    # TIMEIT APPROVED ✅
    # count_nonzero proven to be faster with timeit
    ''' Returns True if the board is full, False otherwise, works only for 3x3 subboards '''
    return (np.count_nonzero(board) == 9)

def notFullLocal(board):
    # TIMEIT APPROVED ✅
    # count_nonzero proven to be faster with timeit
    ''' Returns True if the board is not full, False otherwise, works only for 3x3 subboards '''
    return (np.count_nonzero(board) != 9)

def emptyCellsLocal(board):
    # TIMEIT APPROVED ✅
    # count_nonzero proven to be faster with timeit
    ''' Returns the amount of emtpy cells available in the local board '''
    return (9 - np.count_nonzero(board))

def emptyCellsGlobal(board):
    # TIMEIT APPROVED ✅
    # count_nonzero proven to be faster with timeit
    ''' Returns the amount of emtpy cells available in the global board '''
    return (81 - np.count_nonzero(board))

# def isCorner(coord: tuple) -> bool:
#     # TIMEIT APPROVED ✅
#     ''' 
#     TIME RESULTS SHOWED THAT, AFTER 2billion+ ITERATIONS
#     isCorner took 230 seconds
#     isEdge took 185 seconds
#     coord==(1, 1) took 150 seconds (is center)
#     '''
     
#     return coord in [(0, 0), (0, 2), (2, 0), (2, 2)]

def isEdge(x: int, y: int) -> bool:
    # TIMEIT APPROVED ✅
    ''' 
    TIME RESULTS SHOWED THAT, AFTER 2billion+ ITERATIONS
    isCorner took 230 seconds
    isEdge took 185 seconds
    coord==(1, 1) took 150 seconds (is center)
    '''
     
    return (x+y) % 2 == 1

def centerCoef(board, x, y) -> float:
    # TIMEIT APPROVED ✅
    ''' Given 2 coordinates: x, y, returns a "centerness" coefficient of their position in the board '''
    if (x, y) == (1, 1):
        # Center
        return 1
    if (x+y) % 2 == 1:
        # Edge
        return 0.75
    else:
        # Corner
        return 0.85    

def boardToTuple(board):
    # TIMEIT APPROVED ✅
    if not isinstance(board, np.ndarray):
        raise ValueError("Board being turned to Tuple is not a numpy array!")
    return tuple(map(tuple, board))

def boardToHash(board):
    # TIMEIT APPROVED ✅
    ''' Returns the board as bytes for hashing '''
    return board.tobytes()

# Winnable
def isWinnable(subboard, player):
    # NEEDS TIME IMPROVEMENT 🚨
    # dont use 'for' cycles, just index the 9 boards by hand
    ''' If the player can win in the next move, returns a Tuple with the subboard coordinates for the win
    Returns None otherwise '''
    board = subboard.copy()

    # if isWon(board) is not None:
    #     return None

    for i in range(3):
        for j in range(3):
            if board[i, j] == 0:
                board[i, j] = player
                if isWon(board) == player:
                    return (i, j)
                board[i, j] = 0
    return None

def winnableOne(subboard):
    # TIMEIT APPROVED ✅
    ''' Returns True if the board is winnable by Player 1, False otherwise '''
    return (isWinnable(subboard, player=1) is not None)

def winnableTwo(subboard):
    # TIMEIT APPROVED ✅
    ''' Returns True if the board is winnable by Player -1, False otherwise '''
    return (isWinnable(subboard, player=-1) is not None)

def letsWinInOne(board, move, player):
    # TIMEIT APPROVED ✅
    ''' Returns True if the given move in the super-board leads to a sub-board where the 
    player can win in one move, Returns False otherwise '''    
    letsWin = isWinnable(board[move[0], move[1]], player)
    return letsWin is not None

def winnableBoardFinder(board, player):
    # NEEDS TIME IMPROVEMENT 🚨
    # dont use 'for' cycles, just index the 9 boards by hand
    # also just literally hashing, may need to be relocated to the class
    ''' 
    Returns the coordinates of the subboard where the player can win in the next move 
    Returns None if no such subboard exists 

    WARNING! SHOULD ONLY BE GIVEN THE PLAYABLE BOARDS TO ITERATE THROUGH, IT HAS NO BACKUP CHECKS 
    AND WILL OTHERWISE RETURN ALWAYS A WON BOARD IF THERE IS ONE AT FIRST
    '''

    for i in range(3):
        for j in range(3):
            subboard = board[i, j]
            if isWinnable(subboard, player) is not None:
                return i, j
    return None

def winnableBoardMyself(board):
    # TIMEIT APPROVED ✅
    ''' Returns the coordinates of the subboard where the player can win in the next move 
    Returns None if no such subboard exists '''
    return winnableBoardFinder(board, player=1)

def winnableBoardRival(board):
    # TIMEIT APPROVED ✅
    ''' Returns the coordinates of the subboard where the rival can win in the next move 
    Returns None if no such subboard exists '''
    return winnableBoardFinder(board, player=-1)

# Evaluation
def lineEval(line, player=1):
    # TIMEIT APPROVED ✅
    """ 
    Returns the heuristic value of the given row or column in the subboard.
    """
    empties = line.count(0)

    if empties == 3:
        return 0
    
    player_count = line.count(player)

    if empties == 2:
        return 0.2 if player_count == 1 else -0.2
    
    elif empties == 1:
        return 0.6 if player_count == 2 else (-0.6 if player_count == 0 else 0)
    
    else:
        # print(f"Found a full line at {line}, with {empties} empties")
        if player_count == 3:
            return 1
        elif player_count == 0:
            return -1
        else:
            return 0

def line_mtw(line, player):
    # NEEDS TIMEIT TESTING 🔔
    player_count, opponent_count = line.count(player), line.count(-player)
    return 3 - player_count if opponent_count == 0 else 10

def min_moves_to_win(board: np.ndarray, player: int) -> int:
    # NEEDS TIME IMPROVEMENT 🚨 (If you're actually gonna use it, then just make a hash out of it)
    # make two hash files, for player one and playr minus one like you did with winnables, being board : min_moves (int)
    # y si solo lo vas a usar para la penalty, just make the hash directly with the penalty y olvidate de usar esta
    ''' Returns the minimum amount of moves the player needs to win the board '''
    # Check if board shape is correct
    if board is None or board.shape != (3, 3):
        raise ValueError("The board must be a 3x3 numpy array")
    
    b00, b01, b02, b10, b11, b12, b20, b21, b22 = board[0, 0], board[0, 1], board[0, 2], board[1, 0], board[1, 1], board[1, 2], board[2, 0], board[2, 1], board[2, 2]

    # Rows
    min_moves = min(
        line_mtw((b00, b01, b02), player), line_mtw((b10, b11, b12), player), line_mtw((b20, b21, b22), player), line_mtw((b00, b11, b22), player),
        line_mtw((b00, b10, b20), player), line_mtw((b01, b11, b21), player), line_mtw((b02, b12, b22), player), line_mtw((b20, b11, b02), player)
    )

    return min_moves if min_moves != 10 else None

def min_moves_to_win_penalty(board: np.ndarray, player: int) -> int:
    # NEEDS TIME IMPROVEMENT 🚨 (If you're actually gonna use it, then just make a hash out of it)
    # make two hash files, for player one and playr minus one like you did with winnables, being board : min_moves_penalty (float)
    ''' Returns the enemy board tax / penalty value directly to save time from calling 'if' cycles '''

    # Check if board shape is correct
    if board is None or board.shape != (3, 3):
        raise ValueError("The board must be a 3x3 numpy array")
    
    b00, b01, b02, b10, b11, b12, b20, b21, b22 = board[0, 0], board[0, 1], board[0, 2], board[1, 0], board[1, 1], board[1, 2], board[2, 0], board[2, 1], board[2, 2]

    # Rows
    min_moves = min(
        line_mtw((b00, b01, b02), player), line_mtw((b10, b11, b12), player), line_mtw((b20, b21, b22), player), line_mtw((b00, b11, b22), player),
        line_mtw((b00, b10, b20), player), line_mtw((b01, b11, b21), player), line_mtw((b02, b12, b22), player), line_mtw((b20, b11, b02), player)
    )

    return (1 / ((min_moves)**1.35)) if min_moves != 10 else (-0.25)


# Couple of tests (unadvanced, not using assert and such)
agent = FooFinderAgent()

board_1 = np.array([[1, 1, 1],
                    [0, -1, -1],
                    [0, 0, -1]])  # Player 1 wins on the top row
a1 = agent.get_isWon(board_1)
b1 = agent.get_over_hash(board_1)
c1 = agent.get_playable_hash(board_1)
d1 = agent.get_eval(board_1)
e1 = agent.get_isDraw(board_1)
f1 = agent.get_winnableByOne(board_1)
g1 = agent.get_winnableByMinusOne(board_1)
# h1 = agent.get_bestMove(board_1)

board_2 = np.array([[1, -1, 1],
                    [0, -1, -1],
                    [1, 1, 0]])  # Not Won (winnable by 1 in (1, 0), (2, 2) and by -1 in (1, 0))
a2 = agent.get_isWon(board_2)
b2 = agent.get_over_hash(board_2)
c2 = agent.get_playable_hash(board_2)
d2 = agent.get_eval(board_2)
e2 = agent.get_isDraw(board_2)
f2 = agent.get_winnableByOne(board_2)
g2 = agent.get_winnableByMinusOne(board_2)
# h2 = agent.get_bestMove(board_2)

board_3 = np.array([[1, -1, -1],
                    [-1, -1, 1],
                    [1, 1, -1]])  # Draw
a3 = agent.get_isWon(board_3)
b3 = agent.get_over_hash(board_3)
c3 = agent.get_playable_hash(board_3)
d3 = agent.get_eval(board_3)
e3 = agent.get_isDraw(board_3)
f3 = agent.get_winnableByOne(board_3)
g3 = agent.get_winnableByMinusOne(board_3)
# h3 = agent.get_bestMove(board_3)

def run_hash_tests():
    assert a1 == 1
    assert b1 == True
    assert c1 == False
    assert d1 == 6.4
    assert e1 == False
    assert f1 == set()
    assert g1 == set()

    assert a2 == 0
    assert b2 == False
    assert c2 == True
    assert d2 != 0
    assert abs(d2) < 6.4
    assert e2 == False
    assert f2 == {(1, 0), (2, 2)}
    assert g2 == {(1, 0)}

    assert a3 == 0
    assert b3 == True
    assert c3 == False
    assert d3 == 0
    assert e3 == True
    assert f3 == set()
    assert g3 == set()
       
    print(Style.BRIGHT + Fore.GREEN + "All FooFinder Hash Tests passed successfully! 😄" + Style.RESET_ALL)

# uncomment me to run hash tests
# run_hash_tests()








# OUTDATED BY THE HASH! :(
def isWon(subboard):
    # TIMEIT ACCEPTED ☑️ (Replaced by hashing, but for its purposes it's 100% optimized)
    ''' Returns None if the board is not won, 1 if player 1 won, -1 if player -1 won '''
    # Row 0
    sb_00, sb_01, sb_02 = subboard[0, 0], subboard[0, 1], subboard[0, 2]
    if sb_00 == sb_01 == sb_02 != 0:
        return sb_00
    
    # Row 1
    sb_10, sb_11, sb_12 = subboard[1, 0], subboard[1, 1], subboard[1, 2]
    if sb_10 == sb_11 == sb_12 != 0:
        return sb_10
    
    sb_20 = subboard[2, 0]
    # Save unncessary calcs, by using what we alreasy can

    # Column 1
    if sb_00 == sb_10 == sb_20 != 0:
        return sb_00
    
    # Diagonal BT
    if sb_20 == sb_11 == sb_02 != 0:
        return sb_20
    
    sb_21 = subboard[2, 1]
    # again, save time

    # Check Column 2
    if sb_01 == sb_11 == sb_21 != 0:
        return sb_01
    
    sb_22 = subboard[2, 2]
    # Row 2
    if sb_20 == sb_21 == sb_22 != 0:
        return sb_20
    
    # Column 2
    if sb_02 == sb_12 == sb_22 != 0:
        return sb_02
    
    # Diagonal TB
    if sb_00 == sb_11 == sb_22 != 0:
        return sb_00
    
    return None

def checkBoardWinner(board):
    # TIMEIT ACCEPTED ☑️ (Replaced by hashing, but for its purposes it's 100% optimized)
    ''' Analyzes whether the global board has been won, by a player connecting 3 Won Local Boards 
    Returns 1 if Player 1 has won, -1 if Player -1 has won, None if no one has won '''
    
    # Row 0
    b_00, b_01, b_02 = isWon(board[0, 0]), isWon(board[0, 1]), isWon(board[0, 2])
    if b_00 == b_01 == b_02 != 0:
        return b_00
    
    # Row 1
    b_10, b_11, b_12 = isWon(board[1, 0]), isWon(board[1, 1]), isWon(board[1, 2])
    if b_10 == b_11 == b_12 != 0:
        return b_10
    
    b_20 = isWon(board[2, 0])
    # Save unncessary calcs, by using what we alreasy can

    # Column 0
    if b_00 == b_10 == b_20 != 0:
        return b_00
    
    # Diagonal BT
    if b_20 == b_11 == b_02 != 0:
        return b_20

    b_21 = isWon(board[2, 1]) 
    # again, save time

    # Check Column 1
    if b_01 == b_11 == b_21 != 0:
        return b_01

    b_22 = isWon(board[2, 2])
    # Row 2
    if b_20 == b_21 == b_22 != 0:
        return b_20

    # Column 2
    if b_02 == b_12 == b_22 != 0:
        return b_02
    
    # Diagonal TB
    if b_00 == b_11 == b_22 != 0:
        return b_00
    
    return 0

def canBePlayed(subboard):
    # TIMEIT ACCEPTED ☑️ (Replaced by hashing, but for its purposes it's 100% optimized)
    ''' Returns True if the board is not full and not won, False otherwise
    Meaning it can be played in '''
    return (notFullLocal(subboard)) and (isWon(subboard) is None)

def localBoardEval(localBoard):
    # TIMEIT APPROVED ✅
    ''' 
    Evaluates the local board and returns an evaluation score for it 
    For Non-Won Boards, Balance Ranges Theoretically from -3.6 to 3.6
    For Won Boards, Balance is ± 6.4
    '''
    # TODO If board is on the precomputed hash, then fetch it and return the value!
    # precomputed boards logic

    score = 0

    # Rows
    row1_eval = lineEval((localBoard[0, 0], localBoard[0, 1], localBoard[0, 2]))
    if abs(row1_eval) == 1:
        return 6.4 * row1_eval
    score += row1_eval

    row2_eval = lineEval((localBoard[1, 0], localBoard[1, 1], localBoard[1, 2]))
    if abs(row2_eval) == 1:
        return 6.4 * row2_eval
    score += row2_eval

    row3_eval = lineEval((localBoard[2, 0], localBoard[2, 1], localBoard[2, 2]))
    if abs(row3_eval) == 1:
        return 6.4 * row3_eval
    score += row3_eval

    # Columns
    col1_eval = lineEval((localBoard[0, 0], localBoard[1, 0], localBoard[2, 0]))
    if abs(col1_eval) == 1:
        return 6.4 * col1_eval
    score += col1_eval

    col2_eval = lineEval((localBoard[0, 1], localBoard[1, 1], localBoard[2, 1]))
    if abs(col2_eval) == 1:
        return 6.4 * col2_eval
    score += col2_eval

    col3_eval = lineEval((localBoard[0, 2], localBoard[1, 2], localBoard[2, 2]))
    if abs(col3_eval) == 1:
        return 6.4 * col3_eval
    score += col3_eval

    # Diagonals
    diagTB_eval = lineEval((localBoard[0, 0], localBoard[1, 1], localBoard[2, 2]))
    # If the Local Board is Won, cut and return ±10
    if abs(diagTB_eval) == 1:
        return 6.4 * diagTB_eval
    score += diagTB_eval

    diagBT_eval = lineEval((localBoard[2, 0], localBoard[1, 1], localBoard[0, 2]))
    # If the Local Board is Won, cut and return ±10
    if abs(diagBT_eval) == 1:
        return 6.4 * diagBT_eval
    score += diagBT_eval

    return score
