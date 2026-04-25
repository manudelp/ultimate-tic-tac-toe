import numpy as np
import random
import os
import time
import ast
from typing import List, Tuple, Dict, Any, Union, Optional
from bots.base import BaseAgent
from core.board_utils import is_full, is_edge

"""
depth = 6/5, plain alpha beta
Board Balance = Sum of Local Board Balances
AB-Pruning Minimax? = True
Order Moves? = False!

"""

from bots.base import BaseAgent


class JardiShowAgent(BaseAgent):
    id = 3
    name = "Jardinero"
    icon = "🍀"
    description = "Jardinero is a mischievous plant enthusiast who always has a trick up his sleeve. Watch out, he's here to turn your game into his garden!"
    difficulty = 4

    def reset(self):
        super().reset()
        self.minimax_plays = 0
        self.total_minimax_time = 0

    def load(self):
        super().load()
        
        self.moveNumber = 0
        self.total_minimax_time = 0
        self.minimax_plays = 0
        
        # Minimax Parameters
        self.depth_local = 8 # when btp is not None
        self.depth_global = 7 # when btp is None
        self.time_limit = 10 # in seconds
        
        # Class Sets
        self.over_boards_set = set()
        self.model_over_boards_set = set()
        self.playable_boards_set = set()
        self.model_playable_boards_set = set()
        
        # Hash Up
        self.hash_loading()
        
        self.loaded_up = True

    def action(self, super_board, board_to_play=None):
        self.true_time_start = time.time()
        # print(f"{self.name} begins action, at move number {self.moveNumber}")

        super_board = np.array(super_board, dtype=int)
        rows, cols, *_ = super_board.shape
        global_board_copy = super_board.copy()

        self.updateOverBoards(super_board)
        self.updatePlayableBoards(super_board)

        self.model_over_boards_set = self.over_boards_set.copy()
        self.model_playable_boards_set = self.playable_boards_set.copy()

        # If No One has Played, We Play Center-Center
        if np.count_nonzero(super_board) == 0:
            if self.moveNumber != 0:
                raise ValueError(f"{self.name}, No one has played, but move number is not 0, move number is {self.moveNumber}")
            self.moveNumber += 1
            return 1, 1, 1, 1

        if board_to_play is None:
            # Minimax Move, with Iterative Deepening
            # print(f"{self.name} is thinking with alpha beta... btp is None")
            # minimax with alphabeta pruning
            t0 = time.time()
            minimax_eval, minimax_move = self.alphaBetaModel(
            board=global_board_copy, 
            board_to_play=None, 
            depth=self.depth_global, 
            alpha=float('-inf'), 
            beta=float('inf'), 
            maximizingPlayer=True)

            if minimax_move is not None:
                # print(f"{self.name} chose alpha beta move: {minimax_move}")
                r, c, r_l, c_l = minimax_move
                self.moveNumber += 1
                minimax_time = time.time() - self.true_time_start
                print(f"{self.name} took {minimax_time:.4f}s alpha-beta depth={self.depth_global}, btp=None")
                self.minimax_plays += 1
                self.total_minimax_time += minimax_time
                return r, c, r_l, c_l
            else:
                raise ValueError("{self.name} failed to play with alpha beta, playing randomly... (inital btp was None)")
            
        else:   
            a, b = board_to_play
        subboard = super_board[a, b]

        # minimax with alphabeta pruning
        # print(f"{self.name} is thinking with alpha beta,  btp is ({a}, {b})")
        t0 = time.time()
        minimax_eval, minimax_move = self.alphaBetaModel(
            board=global_board_copy, 
            board_to_play=(a, b), 
            depth=self.depth_local, 
            alpha=float('-inf'), 
            beta=float('inf'), 
            maximizingPlayer=True)
        if minimax_move is not None:
            a, b, r_l, c_l = minimax_move
        else:
            raise ValueError(f"{self.name} failed to play with alpha beta, playing randomly... initial btp was ({a}, {b})")

        self.moveNumber += 1
        minimax_time = time.time() - self.true_time_start
        print(f"{self.name} took {minimax_time:.4f}s alpha-beta depth={self.depth_local}, btp=({a}, {b})")
        self.minimax_plays += 1
        self.total_minimax_time += minimax_time
        return a, b, r_l, c_l

    def hash_loading(self):
        self.hash_over_boards = {}
        self.hash_eval_boards = {}
        self.hash_boards_information = {}

        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        over_boards_path = os.path.join(root_dir, 'data', 'hash_over_boards.txt')
        evaluated_boards_path = os.path.join(root_dir, 'data', 'hash_evaluated_boards.txt')
        board_info_path = os.path.join(root_dir, 'data', 'hash_boards_information.txt')

        # Load the boards using the absolute paths
        self.load_over_boards(over_boards_path)
        self.load_evaluated_boards(evaluated_boards_path)
        self.load_boards_info(board_info_path)


    def randomMove(self, board):
        empty_cells = np.flatnonzero(board == 0)
        print(f"Empty cells: {empty_cells}")

        # Randomly choose an empty cell from the available ones
        chosen_index = np.random.choice(empty_cells)
        c, d = np.unravel_index(chosen_index, board.shape)

        return c, d


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

        # if depth == self.depth:
        #     print(f"Monke! My depth equality check does work")

        # Base case: If we've reached the maximum depth or the game state is terminal (win/loss/draw)
        winner = checkBoardWinner(board)
        if winner != 0:
            if winner == 1:
                return 100_000, None
            elif winner == -1:
                # print(Fore.BLUE + f"{self.name} found a loss in recursion!" + Style.RESET_ALL)
                balance = -100_000 - depth # to prioritize the slowest loss
                return balance, None
        else:
            if depth == 0:
                return self.boardBalance(board), None
            # if boars isOver, but winner == 0, then it must be full, thus balance=0
            elif ((self.countPlayableBoards(board) == 0) or (is_full(board))):
                # print(f"{self.name} found over board (drawn) in recursion!")
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

            for (row, col) in der_playable_boards:
                local_board = board[row, col]
                empty_indices = np.argwhere(local_board == 0)
                
                for submove in empty_indices:
                    local_row, local_col = submove
                    global_moves.append([row, col, int(local_row), int(local_col)])

            if not global_moves:
                raise ValueError(f"Global moves are empty! Conditions were: maxi={maximizingPlayer}, depth={depth}, a={alpha}, b={beta}. The playble boards were {der_playable_boards}\n Current global board was:\n {board} ")

            # order the global moves
        

            if maximizingPlayer:
                max_eval = float('-inf')
                for move in global_moves:
                    
                    # if depth == self.depth:
                    #     if not self.isTrulyPlayable(board, move[0], move[1], move[2], move[3]):
                    #         raise ValueError(f"{self.name} is at call number 0, considering invalid move: {move}")

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

                    # if depth == self.depth:
                    #     if not self.isTrulyPlayable(board, move[0], move[1], move[2], move[3]):
                    #         raise ValueError(f"{self.name} is at call number 0, considering invalid move: {move}")

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

    def generate_global_moves(self, board):
        ''' Given a global board, generates a list of all playable moves 
        in the playable local boards '''
        global_moves = []
        for (row, col) in self.genPlayableBoards(board):
            local_board = board[row, col]
            for submove in np.argwhere(local_board == 0):
                global_moves.append([int(submove[0]), int(submove[1])])
        return global_moves

    def boardBalance(self, board):
        ''' Returns the heuristic value of the board 
        For now it's a sum of the local board evaluations '''
        rows, cols, *_ = board.shape
        balance = 0

        # Auxiliar For Now!
        for r in range(rows):
            for c in range(cols):
                localBoard = board[r, c]
                local_balance = self.get_local_eval(localBoard)
                # Based on which board it is
                if is_edge(r, c):
                    balance += local_balance
                elif (r, c) == (1, 1):
                    balance += 1.5 * local_balance
                else:
                    balance += 1.25 * local_balance

        return round(balance, 4)

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

    def load_evaluated_boards(self, file_path):
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
                    board_hex, heuristic_value = line.strip().split(':')
                    if heuristic_value == "Draw":
                        self.hash_eval_glob_boards[bytes.fromhex(board_hex)] = heuristic_value
                    else:
                        self.hash_eval_glob_boards[bytes.fromhex(board_hex)] = float(heuristic_value)
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Evaluated boards will not be loaded.")

    def get_over_hash(self, board):
        # TIMEIT APPROVED ✅
        ''' If the board is found in the over boards, return True, else False '''
        board_key = board.tobytes()
        return self.hash_over_boards.get(board_key, False)

    def get_playable_hash(self, board):
        # TIMEIT UNSURE 🤔 (yes it would be faster to just call not get_over_hash directly 
        # instead of calling get_playable_hash to call it as a mediator, dont know if its relevant enough)
        ''' Returns True if the board is playable, False otherwise '''
        return not self.get_over_hash(board)

    def get_local_eval(self, board):
        """
        Retrieve the heuristic value of a board from the preloaded dictionary of evaluated boards.
        If the board is not in the dictionary, return None (or handle it as needed).
        """
        board_key = board.tobytes()
        local_eval, _ = self.hash_eval_boards.get(board_key, None)
        if local_eval is None:
            raise ValueError(f"Board {board} not found in evaluated boards.")
        return local_eval

    def get_board_info(self, board):
        ''' Retrieve the heuristic value of a board from the preloaded dictionary of evaluated boards '''
        board_key = board.tobytes()
        score, result, positional_lead, positional_score = self.hash_boards_information.get(board_key, None)
        if score is None or result is None or positional_lead is None or positional_score is None:
            raise ValueError(f"Board {board} not found in evaluated global boards. Info was {score}, {result}, {positional_lead}, {positional_score}")
        return score, result, positional_lead, positional_score

    def get_global_results_eval(self, board):
        ''' Retrieve the heuristic value of a board from the preloaded dictionary of evaluated boards '''
        board_key = board.tobytes()
        results_eval = self.hash_global_results_evals.get(board_key, None)
        if results_eval is None:
            raise ValueError(f"Board {board} not found in evaluated global boards")
        return results_eval

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

    def updateOverBoards(self, board):
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

    def isTrulyPlayable(self, board, move_row, move_col, move_row_local, move_col_local):
        ''' Returns whether or not the move is truly playable, meaning if the space is empty and the board is playable '''
        local_board = board[move_row, move_col]
        return ((local_board[move_row_local, move_col_local] == 0) and (self.get_playable_hash(local_board)))

    def genPlayableBoards(self, board):
        ''' Given the board, generates a set with all the local boards that are still playable '''
        playable_boards = set()
        if self.get_playable_hash(board[0, 0]):
            playable_boards.add((0, 0))
        if self.get_playable_hash(board[0, 1]):
            playable_boards.add((0, 1))
        if self.get_playable_hash(board[0, 2]):
            playable_boards.add((0, 2))
        if self.get_playable_hash(board[1, 0]):
            playable_boards.add((1, 0))
        if self.get_playable_hash(board[1, 1]):
            playable_boards.add((1, 1))
        if self.get_playable_hash(board[1, 2]):
            playable_boards.add((1, 2))
        if self.get_playable_hash(board[2, 0]):
            playable_boards.add((2, 0))
        if self.get_playable_hash(board[2, 1]):
            playable_boards.add((2, 1))
        if self.get_playable_hash(board[2, 2]):
            playable_boards.add((2, 2))

        return playable_boards

    def countPlayableBoards(self, board):
        ''' Returns the number of playable local boards in the global board '''
        count = 0
        if self.get_playable_hash(board[0, 0]):
            count += 1
        if self.get_playable_hash(board[0, 1]):
            count += 1
        if self.get_playable_hash(board[0, 2]):
            count += 1
        if self.get_playable_hash(board[1, 0]):
            count += 1
        if self.get_playable_hash(board[1, 1]):
            count += 1
        if self.get_playable_hash(board[1, 2]):
            count += 1
        if self.get_playable_hash(board[2, 0]):
            count += 1
        if self.get_playable_hash(board[2, 1]):
            count += 1
        if self.get_playable_hash(board[2, 2]):
            count += 1

        return count



# Performance-optimized isWon (early-exit with variable reuse, used in tight minimax loops)
def isWon(subboard):
    sb_00, sb_01, sb_02 = subboard[0, 0], subboard[0, 1], subboard[0, 2]
    if sb_00 == sb_01 == sb_02 != 0:
        return sb_00
    sb_10, sb_11, sb_12 = subboard[1, 0], subboard[1, 1], subboard[1, 2]
    if sb_10 == sb_11 == sb_12 != 0:
        return sb_10
    sb_20 = subboard[2, 0]
    if sb_00 == sb_10 == sb_20 != 0:
        return sb_00
    if sb_20 == sb_11 == sb_02 != 0:
        return sb_20
    sb_21 = subboard[2, 1]
    if sb_01 == sb_11 == sb_21 != 0:
        return sb_01
    sb_22 = subboard[2, 2]
    if sb_20 == sb_21 == sb_22 != 0:
        return sb_20
    if sb_02 == sb_12 == sb_22 != 0:
        return sb_02
    if sb_00 == sb_11 == sb_22 != 0:
        return sb_00
    return 0


def checkBoardWinner(board):
    b_00, b_01, b_02 = isWon(board[0, 0]), isWon(board[0, 1]), isWon(board[0, 2])
    if b_00 == b_01 == b_02 != 0:
        return b_00
    b_10, b_11, b_12 = isWon(board[1, 0]), isWon(board[1, 1]), isWon(board[1, 2])
    if b_10 == b_11 == b_12 != 0:
        return b_10
    b_20 = isWon(board[2, 0])
    if b_00 == b_10 == b_20 != 0:
        return b_00
    if b_20 == b_11 == b_02 != 0:
        return b_20
    b_21 = isWon(board[2, 1])
    if b_01 == b_11 == b_21 != 0:
        return b_01
    b_22 = isWon(board[2, 2])
    if b_20 == b_21 == b_22 != 0:
        return b_20
    if b_02 == b_12 == b_22 != 0:
        return b_02
    if b_00 == b_11 == b_22 != 0:
        return b_00
    return 0
