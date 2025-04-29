import numpy as np
import random
import os
import time
import ast
from colorama import Style, Fore
from typing import List, Tuple, Dict, Any, Union, Optional

"""
depth = iterative_deepening with move re-order, global depth=7, local depth=8, max time to start a new depth is 30 seconds
Board Balance = Sum of Local Board Balances
AB-Pruning Minimax? = True

"""

class BetterItterinoAgent:
    def __init__(self):
        self.name = "Dr. Deepsdale"
        self.icon = "🔨"
        self.transposition_table = {}
        self.moveNumber = 0
        self.depth_local = 6 # when btp is not None
        self.depth_global = 5 # when btp is None
        self.time_limit = 30 # in seconds
        self.total_minimax_time = 0
        self.minimax_plays = 0
        self.hash_over_boards = {}
        self.hash_eval_boards = {}
        self.hash_boards_information = {}

        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # Construct the absolute paths to the files
        over_boards_path = os.path.join(root_dir, 'agents', 'hashes', 'hash_over_boards.txt')
        evaluated_boards_path = os.path.join(root_dir, 'agents', 'hashes', 'hash_evaluated_boards.txt')
        board_info_path = os.path.join(root_dir, 'agents', 'hashes', 'hash_boards_information.txt')

        # Load the boards using the absolute paths
        self.load_over_boards(over_boards_path)
        self.load_evaluated_boards(evaluated_boards_path)
        self.load_boards_info(board_info_path)

        self.over_boards_set = set()
        self.model_over_boards_set = set()
        self.playable_boards_set = set()
        self.model_playable_boards_set = set() 
    
    def __str__(self):
        self.str = f"{self.name}{self.icon}"
        return self.str

    def reset(self):
        self.transposition_table = {}
        if self.moveNumber == 0 and self.minimax_plays == 0 and self.total_minimax_time == 0:
            print(f"First Game, pointless Reset for {self.name}")
            # return
        # if self.minimax_plays == 0:
            # raise ValueError(Style.BRIGHT + Fore.RED + "Reset has been called, it's not the first game but minimax_plays is 0..." + Style.RESET_ALL)
        # average_minimax_time = self.total_minimax_time / self.minimax_plays
        # print(Style.BRIGHT + Fore.MAGENTA + f"\n{self.name} played Minimax {self.minimax_plays} times with an average time of {average_minimax_time:.4f} seconds" + Style.RESET_ALL)
        self.moveNumber = 0
        self.minimax_plays = 0
        self.total_minimax_time = 0

    def action(self, super_board, board_to_play=None):
        self.true_time_start = time.time()
        # print(f"The Architect and the Builder, they arrive calmly from their escalator with a sense of purpose! ({self.name} move number is {self.moveNumber})")

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
            minimax_eval, minimax_move = self.iterative_deepening(global_board_copy, board_to_play, self.depth_global)

            if minimax_move is not None:
                r, c, r_l, c_l = minimax_move
                self.moveNumber += 1
                minimax_time = time.time() - self.true_time_start
                print(Style.BRIGHT + Fore.CYAN + f"{self.name} took {minimax_time:.4f} seconds to play alpha beta with depth {self.depth_global}, btp was None" + Style.RESET_ALL)
                self.minimax_plays += 1
                self.total_minimax_time += minimax_time
                return r, c, r_l, c_l
            else:
                raise ValueError("{self.name} failed to play with alpha beta, playing randomly... (inital btp was None)")
            
        else:   
            a, b = board_to_play
        subboard = super_board[a, b]

        # region HERE IS ALPHA BETA PRUNING WITHOUT ITERATIVE DEEPENING
        # minimax with alphabeta pruning
        # print(f"{self.name} is thinking with alpha beta, not iterative btp is ({a}, {b})")
        t0 = time.time()
        minimax_eval, minimax_move = self.iterative_deepening(global_board_copy, board_to_play, self.depth_local)
        
        if minimax_move is not None:
            r_l, c_l = minimax_move
        else:
            raise ValueError(f"{self.name} failed to play with alpha beta, playing randomly... initial btp was ({a}, {b})")
         
        self.moveNumber += 1
        minimax_time = time.time() - self.true_time_start
        print(Style.BRIGHT + Fore.CYAN + f"{self.name} took {minimax_time:.4f} seconds to play alpha beta with depth {self.depth_local}, btp was ({a}, {b})" + Style.RESET_ALL)
        self.minimax_plays += 1
        self.total_minimax_time += minimax_time
        return a, b, r_l, c_l


    def randomMove(self, board):
        empty_cells = np.flatnonzero(board == 0)
        print(f"Empty cells: {empty_cells}")

        # Randomly choose an empty cell from the available ones
        chosen_index = np.random.choice(empty_cells)
        c, d = np.unravel_index(chosen_index, board.shape)

        return c, d

    def zeroWinnerCheck(self, board, player, board_to_play=None):
        ''' Checks the entire board to find an immediate winning move for the player 
        If found, returns which player it is '''
        board_copy = board.copy()
        if board_to_play is None:
            for r in range(3):
                for c in range(3):
                    subboard = board_copy[r, c]
                    if isPlayable(subboard):
                        for r_l in range(3):
                            for c_l in range(3):
                                if canPlay(subboard, r_l, c_l):
                                    subboard[r_l, c_l] = player
                                    if checkBoardWinner(board_copy) == player:
                                        return r, c, r_l, c_l
                                    subboard[r_l, c_l] = 0
        
        else:
            r, c = board_to_play
            subboard = board_copy[r, c]
            for r_l in range(3):
                for c_l in range(3):
                    if canPlay(subboard, r_l, c_l):
                        subboard[r_l, c_l] = player
                        if checkBoardWinner(board_copy) == player:
                            return r, c, r_l, c_l
                        subboard[r_l, c_l] = 0

        return None

    def iterative_deepening(self, board, board_to_play, max_depth):
        ''' Basic iterative deepening, repositions top move found to index[0] before next call '''
        start_time = time.time()
        moves_to_try = self.generate_moves(board, board_to_play)
        # Turn Back to array
        moves_to_try = np.array(moves_to_try)
        # time_before_tramites = time.time()

        for depth in range(2, max_depth + 1):
            # print(f"{self.name} about to do alpha_beta on depth {depth}, top 2 moves are {moves_to_try[:2]}")
            this_depth_start = time.time()
            # time_tramites = time.time() - time_before_tramites
            # print(f"El time que le tomo a {self.name} hacer los tramites mas alla del alpha beta fue {time_tramites:.4f} seconds")
            try:
                minimax_eval, minimax_move = self.alpha_beta_move(board, board_to_play, depth, float('-inf'), float('inf'), maximizingPlayer=True, start_time=time.time(), moves_to_try=moves_to_try)
            except TimeoutError:
                print(f"Time Limit Exceeded in Iterative Deepening! Had to break the alpha beta at depth {depth}")
                break

            # time_before_tramites = time.time()
            
            if minimax_move is None:
                raise ValueError(f"Minimax Move was None at depth {depth}")
            
            best_eval = minimax_eval
            best_move = minimax_move
            
            if time.time() - start_time >= (self.time_limit - 2):
                print(f"Had to stop iterative deepening, could not start depth {depth} due to time limit")
                break

            # Reposition the best_move at the top of the list
            t_before_reposition = time.time()
            if depth != max_depth:
                # Turn Into a List
                moves_to_try = [move for move in moves_to_try]
                index_to_remove = next((i for i, arr in enumerate(moves_to_try) if np.array_equal(arr, best_move)), None)
                if index_to_remove is not None:
                    del moves_to_try[index_to_remove]
                    moves_to_try.insert(0, best_move)
                    # Turn back into array
                    moves_to_try = np.array(moves_to_try)
                else:
                    raise ValueError(f"Best Move {best_move} not found in moves_to_try!")
            # print(f"Repositioning best move to first place took {self.name} {time.time() - t_before_reposition:.4f} seconds")   
            
            # UNCOMMENT TO SEE TIME PER DEPTH
            # print(f"{self.name} Running Depth {depth} took {time.time() - this_depth_start:.4f} seconds, board_to_play: {board_to_play}")
 
        return best_eval, best_move

    def alpha_beta_move(self, board, board_to_play, depth, alpha, beta, maximizingPlayer, start_time, moves_to_try):
        ''' Executes Minimax with Alpha-Beta Pruning on the board, with recursion depth limited to 'depth' 
        Returns the board evaluation along with the best_move that leads to it '''
        
        # Time Check
        if time.time() - start_time > (self.time_limit):
            raise TimeoutError(f"Time Limit Exceeded in AlphaBetaMove! Board to play was {board_to_play}, depth was {depth}, at start")
        
        # Check Terminal States
        winner = checkBoardWinner(board)
        if winner != 0:
            return winner * 100000, None
        elif depth == 0:
            return self.boardBalance(board), None
        elif self.countPlayableBoards(board) == 0 or isFull(board):
            return 0, None
        
        # If board_to_play is not None (specific local board)
        if board_to_play is not None:
            row, col = board_to_play

            if maximizingPlayer:
                max_eval = float('-inf')
                best_move = None
                for move in moves_to_try:

                    # Time Check
                    if time.time() - start_time > (self.time_limit):
                        raise TimeoutError(f"Time Limit Exceeded in AlphaBetaMove! Board to play was {board_to_play}, depth was {depth}, at recucall")

                    # Simulate Move
                    loc_row, loc_col = move
                    local_to_play = board[row, col]
                    local_to_play[loc_row, loc_col] = 1

                    # Evaluate Move
                    new_board_to_play, new_moves_to_try = self.new_parameters(board, row, col, loc_row, loc_col)
                    eval, _ = self.alpha_beta_move(
                        board, new_board_to_play, depth - 1, alpha, beta,
                        maximizingPlayer=False, start_time=start_time, moves_to_try=new_moves_to_try
                    )

                    # Undo move
                    local_to_play[loc_row, loc_col] = 0

                    # Update max_eval and best_move
                    if eval > max_eval:
                        max_eval = eval
                        best_move = move

                    # Update alpha and check for pruning
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break

                return max_eval, best_move
            
            else:
                min_eval = float('inf')
                best_move = None
                for move in moves_to_try:

                    # Time Check
                    if time.time() - start_time > (self.time_limit):
                        raise TimeoutError(f"Time Limit Exceeded in AlphaBetaMove! Board to play was {board_to_play}, depth was {depth}, at recucall")

                    # Simulate Move
                    loc_row, loc_col = move
                    local_to_play = board[row, col]
                    local_to_play[loc_row, loc_col] = -1

                    # Evaluate Move
                    new_board_to_play, new_moves_to_try = self.new_parameters(board, row, col, loc_row, loc_col)
                    eval, _ = self.alpha_beta_move(
                        board, new_board_to_play, depth - 1, alpha, beta,
                        maximizingPlayer=True, start_time=start_time, moves_to_try=new_moves_to_try
                    )

                    # Undo move
                    local_to_play[loc_row, loc_col] = 0

                    # Update min_eval and best_move
                    if eval < min_eval:
                        min_eval = eval
                        best_move = move

                    # Update beta and check for pruning
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break

                return min_eval, best_move
            
        # If board_to_play is None (whole global board)
        else:
            if maximizingPlayer:
                max_eval = float('-inf')
                best_move = None
                for move in moves_to_try:

                    # Time Check
                    if time.time() - start_time > (self.time_limit):
                        raise TimeoutError(f"Time Limit Exceeded in AlphaBetaMove! Board to play was {board_to_play}, depth was {depth}, at recucall")

                    # Simulate Move
                    row, col, loc_row, loc_col = move
                    local_to_play = board[row, col]
                    local_to_play[loc_row, loc_col] = 1

                    # Evaluate Move
                    new_board_to_play, new_moves_to_try = self.new_parameters(board, row, col, loc_row, loc_col)
                    eval, _ = self.alpha_beta_move(
                        board, new_board_to_play, depth - 1, alpha, beta,
                        maximizingPlayer=False, start_time=start_time, moves_to_try=new_moves_to_try
                    )

                    # Undo move
                    local_to_play[loc_row, loc_col] = 0

                    # Update max_eval and best_move
                    if eval > max_eval:
                        max_eval = eval
                        best_move = move

                    # Update alpha and check for pruning
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break

                return max_eval, best_move

            else:
                min_eval = float('inf')
                best_move = None
                for move in moves_to_try:

                    # Time Check
                    if time.time() - start_time > (self.time_limit):
                        raise TimeoutError(f"Time Limit Exceeded in AlphaBetaMove! Board to play was {board_to_play}, depth was {depth}, at recucall")

                    # Simulate Move
                    row, col, loc_row, loc_col = move
                    local_to_play = board[row, col]
                    local_to_play[loc_row, loc_col] = -1

                    # Evaluate Move
                    new_board_to_play, new_moves_to_try = self.new_parameters(board, row, col, loc_row, loc_col)
                    eval, _ = self.alpha_beta_move(
                        board, new_board_to_play, depth - 1, alpha, beta,
                        maximizingPlayer=True, start_time=start_time, moves_to_try=new_moves_to_try
                    )

                    # Undo move
                    local_to_play[loc_row, loc_col] = 0

                    # Update min_eval and best_move
                    if eval < min_eval:
                        min_eval = eval
                        best_move = move

                    # Update beta and check for pruning
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break

                return min_eval, best_move

    def new_parameters(self, board, row, col, loc_row, loc_col):
        ''' Simulates a move on the board, given the 4d move and the player
        Returns the new_board_to_play and the new_moves_to_try '''
        if self.get_over_hash(board[loc_row, loc_col]):
            board_to_play = None
            moves_to_try = self.generate_global_moves(board)
        else:
            board_to_play = (loc_row, loc_col)
            moves_to_try = np.argwhere(board[loc_row, loc_col] == 0)
        
        return board_to_play, moves_to_try

    def generate_moves(self, board, board_to_play):
        ''' Generates the moves to try given the board and the board_to_play '''
        if board_to_play is None:
            moves_to_try = self.generate_global_moves(board)
        else:
            row, col = board_to_play
            moves_to_try = self.generate_local_moves(board[row, col])
        
        return moves_to_try

    def generate_local_moves(self, board):
        # TIMEIT ACCEPTED ☑️ (Solo se usa por fuera del Minimax, asi que aceptable enough)
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

    def boardBalance(self, board):
        # NEEDS TIMEIT TESTING 🔔
        ''' Returns the heuristic value of the board 
        For now it's a sum of the local board evaluations plus the connectivity of the global board results 
        Calculated using the local eval of the results array '''
        rows, cols, *_ = board.shape
        balance = 0

        lb00_ev, lb01_ev, lb02_ev = self.get_local_eval(board[0, 0]), self.get_local_eval(board[0, 1]), self.get_local_eval(board[0, 2])
        lb10_ev, lb11_ev, lb12_ev = self.get_local_eval(board[1, 0]), self.get_local_eval(board[1, 1]), self.get_local_eval(board[1, 2])
        lb20_ev, lb21_ev, lb22_ev = self.get_local_eval(board[2, 0]), self.get_local_eval(board[2, 1]), self.get_local_eval(board[2, 2])
        
        # FIXME! Yeah this is stupid, its inefficientfor no reason, lo mejor es lo comentado abajo pero bue
        balance += 1.25 * lb00_ev
        balance += lb01_ev
        balance += 1.25 * lb02_ev
        balance += lb10_ev
        balance += 1.5 * lb11_ev
        balance += lb12_ev
        balance += 1.25 * lb20_ev
        balance += lb21_ev
        balance += 1.25 * lb22_ev
        # balance += (1.25*lb00_ev + lb01_ev + 1.25*lb02_ev + lb10_ev + 1.5*lb11_ev + lb12_ev + 1.25*lb20_ev + lb21_ev + 1.25*lb22_ev)

        # FIXME: Replace this by using the get_full_eval_hash to return the tuple (eval, result) from the txt eval hashes, and then use eval above and result down here

        results_array = np.array([[int(lb00_ev/6), int(lb01_ev/6), int(lb02_ev/6)], [int(lb10_ev/6), int(lb11_ev/6), int(lb12_ev/6)], [int(lb20_ev/6), int(lb21_ev/6), int(lb22_ev/6)]])
        results_balance = self.get_local_eval(results_array)
        result_coef = results_balance * ((1 + abs(results_balance))**2.5) * 1.85
        # FIXME! This might put TOO MUCH emphasis on having a won local board... (maybe)
        # Another idea is to reduce the evals of won locals, 6.4 might be too too big, reduce it significantly or else youre forcing to 
        # have the same massive disproportionality with the results balance weight
        
        balance += result_coef

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

def canPlay(board, i, j):
    return board[i, j] == 0

def isFull(board):
    ''' Returns True if the board is full, False otherwise '''
    return np.count_nonzero(board == 0) == 0

def isWon(subboard):
    ''' Returns None if the board is not won, 1 if player 1 won, -1 if player -1 won '''
    rows, cols = subboard.shape
    # Check rows
    for i in range(rows):
        r1, r2, r3 = subboard[i, 0], subboard[i, 1], subboard[i, 2]
        if r1 == r2 == r3 and r1 != 0:
            return r1
    # Check columns
    for i in range(cols):
        c1, c2, c3 = subboard[0, i], subboard[1, i], subboard[2, i]
        if c1 == c2 == c3 and c1 != 0:
            return c1
    # Check diagonals
    if subboard[0, 0] == subboard[1, 1] == subboard[2, 2] != 0:
        return subboard[0, 0]
    if subboard[0, 2] == subboard[1, 1] == subboard[2, 0] != 0:
        return subboard[0, 2]
    return None

def isPlayable(subboard):
    ''' Returns True if the board is not full and not won, False otherwise '''
    return not isFull(subboard) and (isWon(subboard) is None)

def isCorner(coord: tuple) -> bool:
    # TIMEIT APPROVED ✅
    ''' 
    TIME RESULTS SHOWED THAT, AFTER 2billion+ ITERATIONS
    isCorner took 230 seconds
    isEdge took 185 seconds
    coord==(1, 1) took 150 seconds (is center)
    '''
     
    return coord in [(0, 0), (0, 2), (2, 0), (2, 2)]

def isEdge(x: int, y: int) -> bool:
    # TIMEIT APPROVED ✅
    ''' 
    TIME RESULTS SHOWED THAT, AFTER 2billion+ ITERATIONS
    isCorner took 230 seconds
    isEdge took 185 seconds
    coord==(1, 1) took 150 seconds (is center)
    '''
     
    return (x+y) % 2 == 1

def isWon(subboard):
    # TIMEIT APPROVED ✅
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
    
    return 0

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

def playerHasWon(board, player):
    return player == checkBoardWinner(board)

def isWinnable(subboard, player):
    ''' If the player can win in the next move, returns a Tuple with the subboard coordinates for the win
    Returns None otherwise '''
    rows, cols = subboard.shape
    board = subboard.copy()

    for i in range(rows):
        for j in range(cols):
            if board[i, j] == 0:
                board[i, j] = player
                if isWon(board) == player:
                    return (i, j)
                board[i, j] = 0
    return None

def line_mtw(line, player):
    player_count, opponent_count = line.count(player), line.count(-player)
    return 3 - player_count if opponent_count == 0 else 10

def min_moves_to_win(board: np.ndarray, player: int) -> int:
    # Check if board shape is correct
    if board is None or board.shape != (3, 3):
        raise ValueError("The board must be a 3x3 numpy array")
    
    b00, b01, b02, b10, b11, b12, b20, b21, b22 = board[0, 0], board[0, 1], board[0, 2], board[1, 0], board[1, 1], board[1, 2], board[2, 0], board[2, 1], board[2, 2]

    # Rows
    min_moves = min(
        line_mtw((b00, b01, b02), player), line_mtw((b10, b11, b12), player), line_mtw((b20, b21, b22), player),
        
        # Columns
        line_mtw((b00, b10, b20), player), line_mtw((b01, b11, b21), player), line_mtw((b02, b12, b22), player),
        
        # Diagonals
        line_mtw((b00, b11, b22), player), line_mtw((b20, b11, b02), player)
    )

    return min_moves if min_moves != 10 else None

# to test for bot slowness
# OUTDATED BY THE HASH! :(
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



