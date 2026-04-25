import numpy as np
import random
import os
import time
import ast
from colorama import Style, Fore
from typing import List, Tuple, Dict, Any, Union, Optional

"""
Como Jardito, pero has a better heuristic
Heuristica mas completa considerando conectividad de los resultados
Implementing positional scores as well
"""

class FullInfoAgent:
    def __init__(self):
        self.name = "FullInfo"
        self.icon = "📋"
        self.moveNumber = 0
        self.depth_local = 8 # when btp is not None
        self.depth_global = 7 # when btp is None
        self.time_limit = 10 # in seconds
        self.total_minimax_time = 0
        self.minimax_plays = 0
        self.centering_early_time = 0

        # Hash Up
        self.hash_loading()

        self.over_boards_set = set()
        self.model_over_boards_set = set()
        self.playable_boards_set = set()
        self.model_playable_boards_set = set() 
    
    def __str__(self):
        self.str = f"{self.name}{self.icon}"
        return self.str

    def reset(self):
        print(Style.BRIGHT + Fore.LIGHTBLUE_EX + f"{self.name} took centering early time of {self.centering_early_time} seconds" + Style.RESET_ALL)
        self.centering_early_time = 0
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
                # prnt(f"{self.name} chose alpha beta move: {minimax_move}")
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
        print(Style.BRIGHT + Fore.CYAN + f"{self.name} took {minimax_time:.4f} seconds to play alpha beta with depth {self.depth_local}, btp was ({a}, {b})" + Style.RESET_ALL)
        self.minimax_plays += 1
        self.total_minimax_time += minimax_time
        return a, b, r_l, c_l

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

        # Load the boards using the absolute paths
        self.load_winning_boards(winning_boards_path)
        self.load_drawn_boards(draw_boards_path)
        self.load_over_boards(over_boards_path)
        self.load_evaluated_boards(evaluated_boards_path)
        self.load_boards_info(board_info_path)
        self.load_results_board_eval(results_eval_path)
        self.load_winning_results_boards(winning_results_path)
        self.load_draw_results_boards(draw_results_path)


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

        # BCheck Base Case
        (ev_00, res_00, lead_00, score_00), (ev_01, res_01, lead_01, score_01), (ev_02, res_02, lead_02, score_02) = self.get_board_info(board[0, 0]), self.get_board_info(board[0, 1]), self.get_board_info(board[0, 2])
        (ev_10, res_10, lead_10, score_10), (ev_11, res_11, lead_11, score_11), (ev_12, res_12, lead_12, score_12) = self.get_board_info(board[1, 0]), self.get_board_info(board[1, 1]), self.get_board_info(board[1, 2])
        (ev_20, res_20, lead_20, score_20), (ev_21, res_21, lead_21, score_21), (ev_22, res_22, lead_22, score_22) = self.get_board_info(board[2, 0]), self.get_board_info(board[2, 1]), self.get_board_info(board[2, 2])
        results_board = np.array([[res_00, res_01, res_02], [res_10, res_11, res_12], [res_20, res_21, res_22]])
        winner = self.get_winning_result_hash(results_board)
        if winner != 0:
            # TODO: When optimizing for real, make it just return immediately to slightly save more time
            if winner == 1:
                balance = 100_000 + depth # to prioritize the fastest win
            elif winner == -1:
                balance = -100_000 - depth # to prioritize the slowest loss
            else:
                raise ValueError(f"Winner was not 1 or -1, it was {winner}")
            return balance, None
        else:
            # TODO: ISSUE-9403: Faster Draw Hash
            # Se puede hacer mas rapido, pasando el tablero por el hash que ve 0s, 1s, -1s, 2s, y tener el resultadp
            # en terminos de 0, 1, -1 o 2. Si el resultado es 1 o -1, es winner, si es 2, es draw
            # asi no tengo que llamar un winning hash y un draw hash por separado 
            # simplemente llamo a uno, y despues uso variables
            if self.get_draw_result_hash(results_board):
                return 0, None
            elif depth == 0:
                board_balance = self.board_balance(board=board, 
                                                results_array=results_board, 
                                                ev_00=ev_00, ev_01=ev_01, ev_02=ev_02, 
                                                ev_10=ev_10, ev_11=ev_11, ev_12=ev_12, 
                                                ev_20=ev_20, ev_21=ev_21, ev_22=ev_22,
                                                lead_00=lead_00, lead_01=lead_01, lead_02=lead_02,
                                                lead_10=lead_10, lead_11=lead_11, lead_12=lead_12,
                                                lead_20=lead_20, lead_21=lead_21, lead_22=lead_22,
                                                score_00=score_00, score_01=score_01, score_02=score_02,
                                                score_10=score_10, score_11=score_11, score_12=score_12,
                                                score_20=score_20, score_21=score_21, score_22=score_22)
                return board_balance, None

        # No Terminal State Found, keep going and Implement Alpha Beta
        best_move = None

        # Generate moves based on the current state
        if board_to_play is not None:
            row, col = board_to_play
            local_to_play = board[row, col]
            local_moves = np.argwhere(local_to_play == 0)

            if local_moves.size == 0:
                    raise ValueError(f"Local Moves was Empty! Conditions were: maxi={maximizingPlayer}, depth={depth}, move number = {self.moveNumber}, a={alpha}, b={beta}. The local board was {(row, col)} and looked like: {local_to_play}\n Current global board was:\n {board} ")

            # TODO: Uncomment me! I remove center moves
            before_centering_time = time.time()
            if ((self.moveNumber + depth < 12) and (local_moves.size > 1)):
                # Remove the element [1, 1] from the local_moves
                # First, turn 2d array into a list
                local_moves = local_moves.tolist()
                # Then, remove the [1, 1] element
                if [1, 1] in local_moves:
                    local_moves.remove([1, 1])
                # Finally, turn it back into a numpy array
                local_moves = np.array(local_moves)
            time_spent_centering = time.time() - before_centering_time
            self.centering_early_time += time_spent_centering
            
            if local_moves.size == 0:
                    raise ValueError(f"AFTER CENTERING! Local Moves was Empty! Conditions were: maxi={maximizingPlayer}, depth={depth}, move number = {self.moveNumber}, a={alpha}, b={beta}. The local board was {(row, col)} and looked like: {local_to_play}\n Current global board was:\n {board} ")

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

    def generate_global_moves(self, board: np.array):
        ''' Given a global board, generates a list of all playable moves 
        in the playable local boards '''
        global_moves = []
        for (row, col) in self.genPlayableBoards(board):
            local_board = board[row, col]
            for submove in np.argwhere(local_board == 0):
                global_moves.append([int(submove[0]), int(submove[1])])
        return global_moves

    def board_balance(self, board: np.ndarray,
                    results_array: np.ndarray,
                    ev_00: float, ev_01:float, ev_02: float,
                    ev_10: float, ev_11:float, ev_12: float,
                    ev_20: float, ev_21:float, ev_22: float,
                    lead_00: int, lead_01: float, lead_02: float,
                    lead_10: int, lead_11: float, lead_12: float,
                    lead_20: int, lead_21: float, lead_22: float,
                    score_00: float, score_01: float, score_02: float,
                    score_10: float, score_11: float, score_12: float,
                    score_20: float, score_21: float, score_22: float) -> float:
        # NEEDS TIMEIT TESTING 🔔
        ''' Returns the heuristic value of the board 
        For now it's a sum of the local board evaluations plus the connectivity of the global board results 
        Calculated using the local eval of the results array '''
        CORNER_MULT = 1.25
        CENTER_MULT = 1.5
        RESULTS_EVAL_MULT = 3

        balance = (CORNER_MULT*ev_00 + ev_01 + CORNER_MULT*ev_02 + ev_10 + CENTER_MULT*ev_11 + ev_12 + CORNER_MULT*ev_20 + ev_21 + CORNER_MULT*ev_22)

        # DELETEME: DEBUG COMPARISON TO ENSURE THE RESULTS ARE BEING PROPERLY CALCULATED
        results_list_compare = []
        for i in range(3):
            for j in range(3):
                if self.get_draw_hash(board[i, j]):
                    results_list_compare.append(2)
                else:
                    winner = self.get_winner_hash(board[i, j])
                    results_list_compare.append(winner)
        results_list = results_array.flatten().tolist()
        if results_list_compare != results_list:
            raise ValueError(f"Results List Compare and Results Array are different! list is {results_list_compare} vs array is {results_list}. While board was:\n{board}. For the board 1,1, list would be winner={results_list_compare[4]} and array would be winner={self.get_winner_hash(board[i, j])}")
        # DELME ABOVE
        
        res_score = self.get_results_board_eval(results_array)
        result_coef = res_score * RESULTS_EVAL_MULT
        # FIXME! Currently losing! Another idea is to reduce the evals of won locals, 6.4 might be too too big, reduce it significantly or else youre forcing to 
        # have the same massive disproportionality with the results balance weight

        balance += result_coef
        
        return balance
        # return round(balance, 4)

    # region Hashing Functions

    # Winning Loaders
    def load_winning_boards(self, file_path):
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

    def load_winning_results_boards(self, file_path):
        ''' Load the winning boards from a file and store them in a dictionary '''
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, winner = line.strip().split(':')
                    self.hash_winning_results_boards[bytes.fromhex(board_hex)] = int(winner)
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Winning boards will not be loaded.")

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

    # Evaluation Loaders
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

    def load_evaluated_v2_boards(self, file_path):
        ''' Load the evaluated boards from a file and store them in a dictionary '''
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, board_info_str = line.strip().split(':')
                    board_info_tuple = ast.literal_eval(board_info_str)
                    heuristic_value, result = board_info_tuple
                    self.hash_eval_v2_boards[bytes.fromhex(board_hex)] = (float(heuristic_value), int(result))
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Evaluated boards will not be loaded.")

    def load_evaluated_v3_boards(self, file_path):
        ''' Load the evaluated boards from a file and store them in a dictionary '''
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, board_info_str = line.strip().split(':')
                    board_info_tuple = ast.literal_eval(board_info_str)
                    heuristic_value, result = board_info_tuple
                    self.hash_eval_v3_boards[bytes.fromhex(board_hex)] = (float(heuristic_value), int(result))
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

    def load_results_board_eval(self, file_path):
        ''' Load the evaluated boards from a file and store them in a dictionary '''
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, heuristic_value = line.strip().split(':')
                    self.hash_results_boards[bytes.fromhex(board_hex)] = float(heuristic_value)
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Evaluated boards will not be loaded.")

    # Draw Loaders
    def load_drawn_boards(self, file_path):
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

    def load_draw_results_boards(self, file_path):
        ''' Load the winning boards from a file and store them in a dictionary '''
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    board_hex, is_draw = line.strip().split(':')
                    self.hash_draw_results_boards[bytes.fromhex(board_hex)] = (is_draw == 'True')
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found. Winning boards will not be loaded.")

    # Hyphen Numeric Loaders
    def load_HyphenNumeric_boards(self, file):
        ''' Loads the winnable boards from a file and stores them in a dictionary. 
        Each board state is stored as a key (board representated by 2 frozensets with each player's pieces, and the board_to_play).
        They are stored as (board_state, board_to_play) : best_move (represented by a tuple of ints)
        '''
        with open(file, 'r') as f:
            for line in f:
                self.parse_and_store_board_line(line)
                
    def load_HyphenNumeric_boards_rival(self, file):
        ''' Loads the winnable boards from a file and stores them in a dictionary. 
        Each board state is stored as a key (board representated by 2 frozensets with each player's pieces, and the board_to_play).
        They are stored as (board_state, board_to_play) : best_move (represented by a tuple of ints)
        '''
        with open(file, 'r') as f:
            for line in f:
                self.parse_and_store_board_line(line, rival_start=True)

    # Other Loaders
    def load_over_boards(self, file_path):
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

    # Winner Getters
    def get_winner_hash(self, board):
        """
        Retrieve the winner of a board from the preloaded dictionary of winning boards.
        Returns 1 if player 1 won, -1 if player -1 won, or None if there is no winner.
        """
        board_key = board.tobytes()
        return self.hash_winning_boards.get(board_key, 0)

    def get_winning_result_hash(self, board):
        ''' Retrieve the winner of a board from the preloaded dictionary of winning boards '''
        board_key = board.tobytes()
        return self.hash_winning_results_boards.get(board_key, 0)

    def get_winnable_by_one_hash(self, board):
        ''' Returns the set of winning moves for player 1, if the board is winnable '''
        board_key = board.tobytes()
        return self.hash_winnable_boards_by_one.get(board_key, set())

    def get_winnable_by_minus_one_hash(self, board):
        ''' Returns the set of winning moves for player -1, if the board is winnable '''
        board_key = board.tobytes()
        return self.hash_winnable_boards_by_minus_one.get(board_key, set())

    # Eval Getters
    def get_eval_hash(self, board):
        """
        Retrieve the heuristic value of a board from the preloaded dictionary of evaluated boards.
        If the board is not in the dictionary, return None (or handle it as needed).
        """
        board_key = board.tobytes()
        local_eval, _ = self.hash_eval_boards.get(board_key, None)
        if local_eval is None:
            raise ValueError(f"Board {board} not found in evaluated eval boards.")
        return local_eval

    def get_eval_v2_hash(self, board):
        ''' Retrieve the heuristic value of a board from the preloaded dictionary of evaluated boards '''
        board_key = board.tobytes()
        local_eval_v2, _ = self.hash_eval_v2_boards.get(board_key, None)
        if local_eval_v2 is None:
            raise ValueError(f"Board {board} not found in evaluated V2 boards.")
        return local_eval_v2
    
    def get_eval_v3_hash(self, board):
        ''' Retrieve the heuristic value of a board from the preloaded dictionary of evaluated boards '''
        board_key = board.tobytes()
        local_eval_v3, _ = self.hash_eval_v3_boards.get(board_key, None)
        if local_eval_v3 is None:
            raise ValueError(f"Board {board} not found in evaluated V3 boards.")
        return local_eval_v3

    def get_eval_result_v1_hash(self, board):
        ''' Retrieve the result of a board from the preloaded dictionary of evaluated boards '''
        board_key = board.tobytes()
        _, result = self.hash_eval_boards.get(board_key, None)
        if result is None:
            raise ValueError(f"Board {board} not found in evaluated boards.")
        return result
    
    def get_eval_result_v2_hash(self, board):
        ''' Retrieve the result of a board from the preloaded dictionary of evaluated boards '''
        board_key = board.tobytes()
        _, result = self.hash_eval_v2_boards.get(board_key, None)
        if result is None:
            raise ValueError(f"Board {board} not found in evaluated V2 boards.")
        return result
    
    def get_eval_result_v3_hash(self, board):
        ''' Retrieve the result of a board from the preloaded dictionary of evaluated boards '''
        board_key = board.tobytes()
        _, result = self.hash_eval_v3_boards.get(board_key, None)
        if result is None:
            raise ValueError(f"Board {board} not found in evaluated V3 boards.")
        return result

    def get_board_info(self, board):
        ''' Retrieve the heuristic value of a board from the preloaded dictionary of evaluated boards '''
        board_key = board.tobytes()
        score, result, positional_lead, positional_score = self.hash_boards_information.get(board_key, None)
        if score is None or result is None or positional_lead is None or positional_score is None:
            raise ValueError(f"Board {board} not found in evaluated global boards. Info was {score}, {result}, {positional_lead}, {positional_score}")
        return score, result, positional_lead, positional_score

    def get_results_board_eval(self, board):
        ''' Retrieve the heuristic value of a board from the preloaded dictionary of evaluated boards '''
        board_key = board.tobytes()
        hex_key = board_key.hex()
        results_eval = self.hash_results_boards.get(board_key, None)
        if results_eval is None:
            raise ValueError(f"Board not found in results boards!, its hex key was {hex_key}. The board was\n{board}")
        return results_eval

    # Draw Getters
    def get_draw_hash(self, board):
        """
        Retrieve the draw status of a board from the preloaded dictionary of drawn boards.
        Returns True if the board is a draw, False otherwise.
        """
        board_key = board.tobytes()
        return self.hash_draw_boards.get(board_key, False)

    def get_draw_result_hash(self, board):
        ''' Retrieve the winner of a board from the preloaded dictionary of winning boards '''
        board_key = board.tobytes()
        return self.hash_draw_results_boards.get(board_key, False)

    # Hyphen Numeric Getters
    def get_HyphenNumeric_hash(self, board, board_to_play):
        ''' Returns the best move for the given HyphenNumeric board '''
        key, reverse_symmetry_instructions = self.get_HyphenNumeric_parameters(board, board_to_play)
        best_move_raw = self.hash_HyphenNumeric_boards.get(key, None)
        best_move_processed = self.counter_transform_move(best_move_raw, reverse_symmetry_instructions)
        return best_move_processed

    def get_HyphenNumeric_hash_rival(self, board, board_to_play):
        ''' Returns the best move for the given HyphenNumeric board '''
        key, reverse_symmetry_instructions = self.get_HyphenNumeric_parameters(board, board_to_play, rival_start=True)
        best_move_raw = self.hash_HyphenNumeric_boards_rival.get(key, None)
        best_move_processed = self.counter_transform_move(best_move_raw, reverse_symmetry_instructions)
        return best_move_processed

    # Other Getters
    def get_over_hash(self, board):
        ''' If the board is found in the over boards, return True, else False '''
        board_key = board.tobytes()
        return self.hash_over_boards.get(board_key, False)
    
    def get_playable_hash(self, board):
        ''' Returns True if the board is playable, False otherwise '''
        return not self.get_over_hash(board)

    # Move Hashing Auxiliaries Below!
    # Rotations & Reflections 2D
    def rotate_coordinates_2d(self, coordinates: Union[Tuple[int, int], None], rotation_times: int):
        ''' Rotate the board to play by 90 degrees * times, coordinates must be either 0, 1, 2
        So rotations are done performing the (2 - coordinate) operation for the corresponding axis '''
        if coordinates is None:
            return None
        
        a, b = coordinates
        rotation_times %= 4
        
        if rotation_times == 0:
            # 0° rotation
            return a, b
        
        elif rotation_times == 1:
            # 90° rotation
            return b, 2 - a
        
        elif rotation_times == 2:
            # 180° rotation
            return 2 - a, 2 - b
        
        elif rotation_times == 3:
            # 270° rotation
            return 2 - b, a

        raise ValueError(f"Invalid rotation times: {rotation_times}??")

    def reverse_rotation_2d(self, coordinates, rotation_times):
        ''' Reverse the rotation of the coordinates '''
        if coordinates is None:
            return None
        
        a, b = coordinates
        rotation_times %= 4
        
        if rotation_times == 0:
            # 0° rotation
            return a, b
        
        elif rotation_times == 1:
            # 90° rotation
            return 2 - b, a
        
        elif rotation_times == 2:
            # 180° rotation
            return 2 - a, 2 - b
        
        elif rotation_times == 3:
            # 270° rotation
            return b, 2 - a
        
        raise ValueError(f"Invalid rotation times: {rotation_times}??")

    def reflect_coordinates_2d(self, move, reflection_type):
        # Normalize reflection_type to lowercase to handle different cases
        reflection_type = reflection_type.lower()
        a, b = move
        
        if reflection_type == 'none':
            # No reflection
            return a, b
        elif reflection_type == 'horizontal':
            # Horizontal reflection (across the middle row)
            return 2 - a, b
        elif reflection_type == 'vertical':
            # Vertical reflection (across the middle column)
            return a, 2 - b
        elif reflection_type == 'diagonal':
            # Diagonal reflection (top-left to bottom-right)
            return b, a
        elif reflection_type == 'anti-diagonal':
            # Anti-diagonal reflection (top-right to bottom-left)
            return 2 - b, 2 - a
        else:
            raise ValueError(f"Invalid reflection type: {reflection_type}")

    def reverse_reflection_2d(self, move, reflection_type):
        # Applying the same reflection again undoes it (reflections are self-inverse)
        return self.reflect_coordinates_2d(move, reflection_type)

    # Rotations & Reflections 4D
    def rotate_coordinates_4d(self, coordinates: Union[Tuple[int, int, int, int], None], rotation_times: int):
        if coordinates is None:
            return None
        a, b, c, d = coordinates
        rotation_times %= 4
        
        if rotation_times == 0:
            # No rotation
            return a, b, c, d
        elif rotation_times == 1:
            # 90-degree rotation: rotate first two coordinates (a, b) and last two coordinates (c, d)
            return c, d, a, b
        elif rotation_times == 2:
            # 180-degree rotation: swap (a, b) and (c, d)
            return 2 - a, 2 - b, 2 - c, 2 - d
        elif rotation_times == 3:
            # 270-degree rotation: rotate in the opposite direction (c, d) and (a, b)
            return d, c, b, a
        else:
            raise ValueError(f"Invalid rotation time: {rotation_times}")

    def reverse_rotation_4d(self, move, rotation_times):
        # Reverse the rotation by performing the opposite of the given rotation.
        return self.rotate_coordinates_4d(move, (4 - rotation_times) % 4)

    def reflect_coordinates_4d(self, move, reflection_type):
        reflection_type = reflection_type.lower()
        a, b, c, d = move

        if reflection_type == 'none':
            # No reflection
            return a, b, c, d
        elif reflection_type == 'horizontal':
            # Reflect across the first two coordinates (flip a, b)
            return 2 - a, 2 - b, c, d
        elif reflection_type == 'vertical':
            # Reflect across the last two coordinates (flip c, d)
            return a, b, 2 - c, 2 - d
        elif reflection_type == 'diagonal':
            # Reflect across the plane swapping (a, c) and (b, d)
            return c, d, a, b
        elif reflection_type == 'anti-diagonal':
            # Reflect across the plane swapping (b, d) and (a, c)
            return d, c, b, a
        else:
            raise ValueError(f"Invalid reflection type: {reflection_type}")

    def reverse_reflection_4d(self, move, axis):
        ''' Apply inverse reflection to a move '''
        return self.reflect_coordinates_4d(move, axis)

    # DEPRECATED Board Symmetry Methods
    def rotate_board(self, board, times):
        ''' Rotate the board by 90 degrees * times '''
        for _ in range(times):
            board = np.rot90(board, axes=(2, 3))
        return board

    def reflect_board(self, board, axis):
        ''' Reflects the board along the specified axis '''
        if axis == "none":
            return board
        elif axis == "horizontal":
            return np.flip(board, axis=2)
        elif axis == "vertical":
            return np.flip(board, axis=3)
        elif axis == "diagonal":
            return np.flip(board, axis=(2, 3))
        elif axis == "anti-diagonal":
            return np.flip(board, axis=(1, 2))

    # Hyphen Numeric Hash Processing Functions
    def get_HyphenNumeric_parameters(self, board: np.array, board_to_play: Union[Tuple[int, int], None], rival_start=False):
        ''' 
        Returns the key for the HyphenNumeric dictionary, checking all symmetrical variations
        to match the stored key format, and also outputs reverse transformations.
        '''
        # Rotations
        for rotations in range(4):  # Four rotations
            processed_moves_1 = set()
            processed_moves_2 = set()
            raw_moves_player_1, raw_moves_player_2 = self.board_to_moves_list(board)
            
            # Move Rotation
            for move in raw_moves_player_1:
                if len(move) != 4:
                    raise ValueError(f"Invalid move player 1: {move}")
                rotated_move = self.rotate_coordinates_4d(move, rotations)
                processed_moves_1.add(rotated_move)
                
            for move in raw_moves_player_2:
                if len(move) != 4:
                    raise ValueError(f"Invalid move player -1: {move}")
                rotated_move = self.rotate_coordinates_4d(move, rotations)
                processed_moves_2.add(rotated_move)
            
            # Board to Play
            rotated_board_to_play = self.rotate_coordinates_2d(coordinates=board_to_play, rotation_times=rotations)

            # Reflections
            for reflection in ['none', 'horizontal', 'vertical', 'diagonal', 'anti-diagonal']:
                final_moves_1 = set()
                final_moves_2 = set()
                
                # Move Reflection
                for move in processed_moves_1:
                    if len(move) != 4:
                        raise ValueError(f"Invalid move p1 rotated: {move}")
                    reflected_move = self.reflect_coordinates_4d(move, reflection)
                    final_moves_1.add(reflected_move)
                    
                for move in processed_moves_2:
                    if len(move) != 4:
                        raise ValueError(f"Invalid move p2 rotated: {move}")
                    reflected_move = self.reflect_coordinates_4d(move, reflection)
                    final_moves_2.add(reflected_move)
                
                # Board to Play
                reflected_board_to_play = self.reflect_coordinates_2d(rotated_board_to_play, reflection)
                moves_tuple = (final_moves_1, final_moves_2)
                board_key_player_1, board_key_player_2 = self.list_of_tuples_to_HyphenNumeric_str_frozensets(moves_tuple)
                                
                # Construct the hash key with this version
                key = ((board_key_player_1, board_key_player_2), reflected_board_to_play)
                # print(Fore.LIGHTGREEN_EX + f"\nWhile the transposition table looks as such:\n{self.hash_HyphenNumeric_boards}" + Style.RESET_ALL)
                # print(Fore.LIGHTMAGENTA_EX + f"Attempting the key: \n{key}\nwhere rotation = {rotations} and reflection = {reflection}" + Style.RESET_ALL)

                # Check key in hash
                if not rival_start:
                    if key in self.hash_HyphenNumeric_boards:
                        return key, (rotations, reflection)  
                else:
                    if key in self.hash_HyphenNumeric_boards_rival:
                        return key, (rotations, reflection)
                
        return None, None

    def counter_transform_move(self, move: Tuple[int, int, int, int], transformation: Tuple):
        ''' Reverse the transformation to retrieve the original move coordinates '''
        if not transformation:
            return move
        
        rotations, reflection = transformation
        counter_move = move

        # Apply inverse reflection first
        if reflection:
            counter_move = self.reverse_reflection_4d(counter_move, reflection)

        # Apply inverse rotation
        if rotations:
            counter_move = self.reverse_rotation_4d(counter_move, rotations)

        return counter_move

    def board_to_moves_list(self, board) -> Tuple[Tuple[Tuple[int, int, int, int], ...], Tuple[Tuple[int, int, int, int], ...]]:
        ''' Takes a board, and returns 2 tuples, each with N tuples inside '''
        player1_pieces = []
        player_minus1_pieces = []

        for i in range(3):
            for j in range(3):
                for k in range(3):
                    for l in range(3):
                        if board[i, j, k, l] == 1:
                            player1_pieces.append((i, j, k, l))
                        elif board[i, j, k, l] == -1:
                            player_minus1_pieces.append((i, j, k, l))

        return (player1_pieces, player_minus1_pieces)

    def list_of_tuples_to_HyphenNumeric_str_frozensets(self, piece_lists_tuple):
        ''' Convert the list of tuples to the HyphenNumeric format '''
        player_1, player_minus1 = piece_lists_tuple
        player_1_list, player_minus1_list = [], []
        
        for move in player_1:
            i, j, k, l = move
            player_1_list.append(f"{i}_{j}_{k}_{l}")
            
        for move in player_minus1:
            i, j, k, l = move
            player_minus1_list.append(f"{i}_{j}_{k}_{l}")
            
        return (frozenset(player_1_list), frozenset(player_minus1_list))

    def get_quick_board_key(self, board):
        moves1, moves_minus1 = self.board_to_moves_list(board)
        return self.list_of_tuples_to_HyphenNumeric_str_frozensets((moves1, moves_minus1))

    def parse_and_store_board_line(self, line, rival_start=False):
        ''' Parse a line from the file and store the board and its best move '''
        # Get the data
        key_part, move_part = line.strip().split(" : ")
        
        # Board
        board_part, board_to_play_str = key_part.split(", ")
        if rival_start:
            board_key_part = self.parse_board_key_rival(board_part)
        else:
            board_key_part = self.parse_board_key(board_part)

        # Board to play
        if board_to_play_str == 'None':
            board_to_play = None
        else:
            board_to_play = tuple(map(int, board_to_play_str.split("_")))

        # Key is Ready
        full_key = (board_key_part, board_to_play)
        
        # Best Move
        best_move = tuple(map(int, move_part.split("_")))
        
        if rival_start:
            self.hash_HyphenNumeric_boards_rival[full_key] = best_move
        else:
            self.hash_HyphenNumeric_boards[full_key] = best_move

    def parse_board_key(self, board_str):
        ''' Convert the HyphenNumeric string back to a canonical key '''
        pieces = board_str.split("__")
        player1_pieces = set(pieces[i] for i in range(len(pieces)) if i % 2 == 0)
        player_minus1_pieces = set(pieces[i] for i in range(len(pieces)) if i % 2 != 0)

        # Build the frozenset for the key
        return frozenset(player1_pieces), frozenset(player_minus1_pieces)

    def parse_board_key_rival(self, board_str):
        ''' Convert the HyphenNumeric string back to a canonical key '''
        pieces = board_str.split("__")
        player1_pieces = set(pieces[i] for i in range(len(pieces)) if i % 2 != 0)
        player_minus1_pieces = set(pieces[i] for i in range(len(pieces)) if i % 2 == 0)

        # Build the frozenset for the key
        return frozenset(player1_pieces), frozenset(player_minus1_pieces)

    # endregion

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



