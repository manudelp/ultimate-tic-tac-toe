import numpy as np
import random
import os
import time
import ast
from typing import Union, Tuple
from colorama import Style, Fore
from typing import List, Tuple, Dict, Any, Union, Optional

"""
depth = iterative_deepening
Board Balance = Sum of Local Board Balances
AB-Pruning Minimax? = True

"""

class MonkeyAgent:
    def __init__(self):
        self.id = 5
        self.name = "Monkey"
        self.icon = "🙈"
        self.description = "Monke"
        self.difficulty = 1
        self.loaded_up = False
        
        # Temporary to not break
        # self.load()

    def __str__(self):
        self.str = f"{self.name}{self.icon}"
        return self.str

    def load(self):
        ''' Loads all the class elements and hashes for the agent to be ready for a game or set of games 
        To be called at most at the start of every game, ideally at the start of every set of games so as to not waste much time '''

        print(Style.BRIGHT + Fore.LIGHTBLUE_EX + f"Loading {self.name}..." + Style.RESET_ALL)
        
        # Game Track
        self.moveNumber = 0
        self.total_minimax_time = 0
        self.minimax_plays = 0
        
        # Parameters
        self.time_limit = 20 # in seconds
        # self.depth = 6

        # Class Sets
        self.over_boards_set = set()
        self.model_over_boards_set = set()
        self.playable_boards_set = set()
        self.model_playable_boards_set = set() 
        
        # Hash Up
        self.hash_loading()
        
        # Register Load
        self.loaded_up = True

    def reset(self):
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

    def action(self, board, board_to_play=None):
        self.start_time = time.time()
        print(f"{self.name} begins action, move number to play: {self.moveNumber}")

        board = np.array(board, dtype=int)
        rows, cols, *_ = board.shape
        global_board_copy = board.copy()

        self.updateOverBoards(board)
        self.updatePlayableBoards(board)

        self.model_over_boards_set = self.over_boards_set.copy()
        self.model_playable_boards_set = self.playable_boards_set.copy()

        # Play Center if first move
        if isEmpty(board):
            self.moveNumber += 1
            return 1, 1, 1, 1

        # Minimax

        if board_to_play is None:
            moves_to_try = self.generate_global_moves(board)

            t_before_order = time.time()
            # TODO: Order Moves in action, test if Phase 1 time gets better or worse
            # unordered_moves = self.generate_global_moves(board)
            # moves_to_try = self.order_moves(board, unordered_moves)
            print(f"Ordering moves for Monkey when btp was None took {time.time() - t_before_order:.4f} seconds")

            # Call Iterative Deepening
            best_move = self.iterative_deepening(board, board_to_play, moves_to_try)

            if best_move is None:
                raise ValueError("Iterative Deepening Failed! Board to play was None!")
            
            global_row, global_col, local_row, local_col = best_move

        else:
            global_row, global_col = board_to_play
            moves_to_try = self.generate_local_moves(board[global_row, global_col])

            t_before_order = time.time()
            # TODO: Order moves in Action, test if Phase 1 time gets better or worse
            # unordered_moves = self.generate_local_moves(board[global_row, global_col])
            # moves_to_try = self.order_moves(board[global_row, global_col], unordered_moves)
            print(f"Ordering moves for Monkey when btp was not None took {time.time() - t_before_order:.4f} seconds")

            # Call Iterative Deepening
            best_move = self.iterative_deepening(board, board_to_play, moves_to_try)

            if best_move is None:
                raise ValueError("Iterative Deepening Failed! Board to play was not None!")
            
            local_row, local_col = best_move

        if global_row is None or global_col is None or local_row is None or local_col is None:
            raise ValueError("Best Move was None! This is being printed at the end of action, after running the minimax...")

        self.moveNumber += 1
        minimax_time = time.time() - self.start_time
        print(Style.BRIGHT + Fore.CYAN + f"{self.name} took {minimax_time:.4f} seconds to play alpha beta with depth {self.depth_global}, btp was {board_to_play}" + Style.RESET_ALL)
        self.minimax_plays += 1
        self.total_minimax_time += minimax_time
        return global_row, global_col, local_row, local_col

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
        self.load_boards_info(board_info_path)
        self.load_results_board_eval(results_eval_path)
        self.load_winning_results_boards(winning_results_path)
        self.load_draw_results_boards(draw_results_path)
        self.load_winnable_boards_one(winnable_boards_one_path)
        self.load_winnable_boards_minus_one(winnable_boards_minus_one_path)



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

    def iterative_deepening(self, board: np.ndarray, board_to_play: Union[Tuple[int, int], None], moves_to_try: list, 
        initial_depth_start=3, initial_depth_end=5, iterative_depth_start=7, quiescence_depth=9, 
        list_cutoff_regular=0.2, list_cutoff_long=0.24, list_cutoff_longest=0.28, 
        quiescence_remaining_time=2, quiescence_moves=4):
        # TIME DEVELOPING ⚙️
        if board_to_play is not None:
            board_to_play = (int(board_to_play[0]), int(board_to_play[1]))

        """ Runs multiple iterations of the minimax Alpha Beta Pruning algorithm with increasing depth until the time limit is reached.
        To decide what the best move for the player will be. 
        Starts out running trials with low depths to re-sort and downsize the moves_to_try list
        Then runs traditional iterative deepening with the reduced ordered list, re-assigning the first position to the best_move found in each iteration, and pushing all other moves 1 index to the right to pass on for the next alpha-beta call
        Finally, when remaining time is low, runs a quiescense search-like iteration on a much higher depth with the first few moves of the final list, to determine which of the top candidates is best.
        Returns the best move found in the last iteration after this entire process.

        Args:
            board (np.ndarray): Current state of the board, comprised of a 3x3 grid of 3x3 local tic tac toe boards, as a 4D Numpy Array (3x3x3x3)
            board_to_play (Union[Tuple[int, int], None]): None if the next board to play can be arbitrarily chosen, otherwise a tuple with the 2D global coordinates of the local board to play in

            moves_to_try (list): A list of the possible moves to be evaluated as the next move, a list of move arrays.
            The individual moves inside the list can be given as size-4 arrays if the board_to_play is None, or size-2 arrays if the board_to_play is specified, since the first 2 coordinates are already defined by board_to_play
            (The Alpha Beta Functions are already designed to perfectly deal with this, if they receive board_to_play as None they are ready for size-4 arrays, if they receive board_to_play=(a, b) they are ready to deal with size-2 arrays)
            There is no need to do anything differently when moves_to_try has size-4 elements or size-2 elements. The process of this function only consists on sorting and downsizing the list, regardless of the size of the arrays inside it

            initial_depth_start (int, optional): The first depth level to start iterating the 'for' loops in the moves_to_try sorting & downsizing process. 
            Defaults to 2 (because for now, that's the example values I'm trying out, I will adjust them through trial & error later).
            
            initial_depth_end (int, optional): The highest depth that will be reached in the moves_to_try sorting & downsizing process, before moving on to the traditional iterative deepening. 
                                               Defaults to 5 (because for now, that's the example values I'm trying out, I will adjust them through trial & error later).
            
            iterative_depth_start (int, optional): First depth for the iterative deepening process, the one which returns the best_move and relocates it to the first index of the list. 
                                                   Defaults to 7 (because for now, that's the example values I'm trying out, I will adjust them through trial & error later).
            
            quiescence_depth (int, optional): The high depth that will be used for the quiescence search with the few top candidates, after remaining time is low. 
                                              Defaults to 10 (because for now, that's the example values I'm trying out, I will adjust them through trial & error later).

            list_cutoff_regular (float, optional): The percentage of the bottom elements of the newly sorted list to be cut-off after each initial-phase low-depth 'for' loop with the new move evals.
                                                   Applicable when length of the list is between 0 and 40. Defaults to 0.2 (because for now, that's the example values I'm trying out, I will adjust them through trial & error later).
            
            list_cutoff_long (float, optional): The percentage of the bottom elements of the newly sorted list to be cut-off after each initial-phase low-depth 'for' loop with the new move evals.
                                                Applicable when length of the list is between 41 and 50. Defaults to 0.24 (because for now, that's the example values I'm trying out, I will adjust them through trial & error later).
            
            list_cutoff_longest (float, optional): The percentage of the bottom elements of the newly sorted list to be cut-off after each initial-phase low-depth 'for' loop with the new move evals.
                                                   Applicable when length of the list is higher than 50. Defaults to 0.28 (because for now, that's the example values I'm trying out, I will adjust them through trial & error later).

            quiescence_remaining_time (float, optional): The amount of remaining time for iteration after which Quiescence Search is activated, when remaining time (calculated with self.time_limit - (time.time() - self.start_time)) is lower than quiescence_remaining_time. 
                                                         Defaults to 2 (because for now, that's the example values I'm trying out, I will adjust them through trial & error later).
            
            quiescence_moves (int, optional): The amount of top candidates that will be picked from the last version of the moves_to_try list when quiescense search mode is activated, 
                                              By doing moves_to_try[:quiescense_moves]. Defaults to 4 (because for now, that's the example values I'm trying out, I will adjust them through trial & error later).

        Returns:
            best_move (np.array or tuple): The best_move. Tuple of length 4 with global coords if btp=None, otherwise length 2 with the local coords only.
        """

        # Timer
        start_time = time.time()

        print(f"Initial length of moves_to_try: {len(moves_to_try)}, moves are: {moves_to_try}")

        # Phase 1: Initial sorting and downsizing
        for depth in range(initial_depth_start, initial_depth_end + 1):
            move_evals = []
            
            # Evaluate moves
            for move in moves_to_try:
                move_copy = move.copy()
                eval = self.alpha_beta_eval(board, board_to_play, depth, float('-inf'), float('inf'), True, start_time, [move_copy])
                # TODO: Si esto tarda mucho, replace it con codigo que instead haga el for, simule cada jugada, 
                # y llame alpha_beta_eval directo con minimizing player, depth-1 y reply_moves (generada en base a la move hecha con self.generate_moves)
                move_evals.append((move, eval))
            
            # Sort moves by evaluation (highest to lowest)
            move_evals.sort(key=lambda x: x[1], reverse=True)
            
            # Determine cutoff percentage
            if len(moves_to_try) > 50:
                cutoff_percentage = list_cutoff_longest
            elif len(moves_to_try) > 40:
                cutoff_percentage = list_cutoff_long
            else:
                cutoff_percentage = list_cutoff_regular
            
            # Calculate moves_to_try based on cutoff
            moves_ordered = [move for move, _ in move_evals]
            num_to_delete = int(cutoff_percentage * len(moves_ordered))  # Round down
            num_to_keep = len(moves_ordered) - num_to_delete
            moves_to_try = moves_ordered[:num_to_keep]

        # Inter-Phase Check! If there is already a winning move, no need to keep iterating
        best_move, best_eval = move_evals[0]
        if best_eval > 90_000:
            print(f"Already found a winning move in Phase 1: {best_move} with evaluation: {best_eval}")
            return best_move

        print(f"Finishing Phase 1 for Monkey took: {time.time() - start_time:.4f} seconds")
        print(f"After Phase 1, moves_to_try has length: {len(moves_to_try)}, moves are: {moves_to_try}")

        # Phase 2: Iterative Deepening with Best Move Reindexing
        depth = iterative_depth_start
        t0 = time.time()

        while depth < quiescence_depth:
            t_this_depth = time.time()
            # Check remaining time
            remaining_time = self.time_limit - (time.time() - start_time)
            if remaining_time <= quiescence_remaining_time:
                # FIXME Improve this based on how long quiescence search can take, foofinder will consider btp scenarios differently
                break  # Transition to quiescence search if time is low

            print(f"Monkey calling alpha_beta_move on phase 2 with depth-{depth} with the moves: {moves_to_try}")
            
            # Step 1: Run alpha_beta_move with the current depth
            current_eval, current_best_move = self.alpha_beta_move(
                board, board_to_play, depth, float('-inf'), float('inf'), True, start_time, moves_to_try
            )
            
            # Step 2: Update best move and evaluation from current depth
            if current_best_move is not None:
                best_move = current_best_move
                best_eval = current_eval

                # Step 3: Reorder moves_to_try, placing the best move at index 0
                index_to_remove = next((i for i, arr in enumerate(moves_to_try) if np.array_equal(arr, current_best_move)), None)
                if index_to_remove is not None:
                    del moves_to_try[index_to_remove]
                    moves_to_try.insert(0, current_best_move)
                else:
                    raise ValueError(f"Best Move {current_best_move} not found in moves_to_try!")
            else:
                raise ValueError(f"Alpha Beta Move returned None! At depth: {depth} where moves_to_try was: {moves_to_try}")

            print(f"Monkey Running Iter Deep at depth {depth} took {time.time() - t_this_depth:.4f} seconds, board_to_play: {board_to_play}")

            if best_eval > 90_000:
                print(f"Already found a winning move inside Phase 2: {best_move} with evaluation: {best_eval}")
                return best_move

            # Move to next depth
            depth += 1

        print(f"Phase2 Iterative Deepening took a total time of {time.time() - t0:.4f} seconds. Maximum Depth Reached: {depth - 1}")

        # Inter-Phase Check! If there is already a winning move, no need to keep iterating
        if best_eval > 90_000:
            print(Style.BRIGHT + Fore.RED + f"THIS SHOULDN'T GET PRINTED!!" + Style.RESET_ALL + f" Already found a winning move after Phase 2: {best_move} with evaluation: {best_eval}")
            return best_move
        
        print(f"Entering Quiessence Search with remaining time: {remaining_time:.4f} seconds")
        t2 = time.time()


        # Phase 3: Quiescence Search for Final Move Refinement
        # remaining_time = self.time_limit - (time.time() - start_time)
        # if remaining_time <= quiescence_remaining_time:

        # Limit moves_to_try to the top few candidates for quiescence search
        moves_to_try = moves_to_try[:quiescence_moves]
        print(f"Monkey gonna quiescense search the moves: {moves_to_try}")
        
        # Run alpha_beta_move at quiescence depth on the top candidates
        quiescence_eval, quiescence_move = self.alpha_beta_move(
            board, board_to_play, quiescence_depth, float('-inf'), float('inf'), True, start_time, moves_to_try
        )

        if quiescence_move is not None:
            print(f"Quiescence search reached depth {quiescence_depth} and found a move!")
            best_move = quiescence_move
            best_eval = quiescence_eval
        else:
            raise ValueError("Quiescence Search returned None")

        print(f"Quiescense Search took a total time of: {time.time() - t2:.4f} seconds")

        # Return the final best move after all phases
        print(f"After Iterative Deepening, best move found was: {best_move} with evaluation: {best_eval}")
        return best_move

    def alpha_beta_eval(self, board, board_to_play, depth, alpha, beta, maximizingPlayer, start_time, moves_to_try):
        ''' Executes Minimax with Alpha-Beta Pruning on the board, with recursion depth limited to 'depth' 
        Returns only the evaluation of the board '''

        # Check Terminal States
        winner = checkBoardWinner(board)
        if winner != 0:
            return winner * 100000
        elif depth == 0:
            return self.boardBalance(board)
        elif self.countPlayableBoards(board) == 0 or isFull(board):
            return 0

        # If board_to_play is not None (specific local board)
        if board_to_play is not None:
            row, col = board_to_play

            if maximizingPlayer:
                max_eval = float('-inf')
                for move in moves_to_try:

                    # Simulate Move
                    loc_row, loc_col = move
                    local_to_play = board[row, col]
                    local_to_play[loc_row, loc_col] = 1

                    # Evaluate Move
                    new_board_to_play, new_moves_to_try = self.new_parameters(board, loc_row, loc_col)
                    eval = self.alpha_beta_eval(
                        board, new_board_to_play, depth - 1, alpha, beta,
                        maximizingPlayer=False, start_time=start_time, moves_to_try=new_moves_to_try
                    )

                    # Undo move
                    local_to_play[loc_row, loc_col] = 0

                    # Update max_eval and best_move
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)

                    # Update alpha and check for pruning
                    if beta <= alpha:
                        break

                return max_eval

            else:
                min_eval = float('inf')
                for move in moves_to_try:

                    # Simulate Move
                    loc_row, loc_col = move
                    local_to_play = board[row, col]
                    local_to_play[loc_row, loc_col] = -1

                    # Evaluate Move
                    new_board_to_play, new_moves_to_try = self.new_parameters(board, loc_row, loc_col)
                    eval = self.alpha_beta_eval(
                        board, new_board_to_play, depth - 1, alpha, beta,
                        maximizingPlayer=True, start_time=start_time, moves_to_try=new_moves_to_try
                    )

                    # Undo move
                    local_to_play[loc_row, loc_col] = 0 

                    # Update min_eval and best_move
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)

                    # Update beta and check for pruning
                    if beta <= alpha:
                        break

                return min_eval

        # If board_to_play is None (whole global board)
        else:
            if maximizingPlayer:
                max_eval = float('-inf')
                for move in moves_to_try:

                    # Simulate Move
                    row, col, loc_row, loc_col = move
                    local_to_play = board[row, col]
                    local_to_play[loc_row, loc_col] = 1

                    # Evaluate Move
                    new_board_to_play, new_moves_to_try = self.new_parameters(board, loc_row, loc_col)
                    eval = self.alpha_beta_eval(
                        board, new_board_to_play, depth - 1, alpha, beta,
                        maximizingPlayer=False, start_time=start_time, moves_to_try=new_moves_to_try
                    )

                    # Undo move
                    local_to_play[loc_row, loc_col] = 0

                    # Update max_eval and best_move
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)

                    # Update alpha and check for pruning
                    if beta <= alpha:
                        break

                return max_eval

            else:
                min_eval = float('inf')
                for move in moves_to_try:

                    # Simulate Move
                    row, col, loc_row, loc_col = move
                    local_to_play = board[row, col]
                    local_to_play[loc_row, loc_col] = -1

                    # Evaluate Move
                    new_board_to_play, new_moves_to_try = self.new_parameters(board, loc_row, loc_col)
                    eval = self.alpha_beta_eval(
                        board, new_board_to_play, depth - 1, alpha, beta,
                        maximizingPlayer=True, start_time=start_time, moves_to_try=new_moves_to_try
                    )

                    # Undo move
                    local_to_play[loc_row, loc_col] = 0

                    # Update min_eval and best_move
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)

                    # Update beta and check for pruning
                    if beta <= alpha:
                        break

                return min_eval

    def alpha_beta_move(self, board, board_to_play, depth, alpha, beta, maximizingPlayer, start_time, moves_to_try):
        ''' Executes Minimax with Alpha-Beta Pruning on the board, with recursion depth limited to 'depth' 
        Returns the board evaluation along with the best_move that leads to it '''
         
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

                    # Simulate Move
                    loc_row, loc_col = move
                    local_to_play = board[row, col]
                    local_to_play[loc_row, loc_col] = 1

                    # Evaluate Move
                    new_board_to_play, new_moves_to_try = self.new_parameters(board, loc_row, loc_col)
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

                    # Simulate Move
                    loc_row, loc_col = move
                    local_to_play = board[row, col]
                    local_to_play[loc_row, loc_col] = -1

                    # Evaluate Move
                    new_board_to_play, new_moves_to_try = self.new_parameters(board, loc_row, loc_col)
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

                    # Simulate Move
                    row, col, loc_row, loc_col = move
                    local_to_play = board[row, col]
                    local_to_play[loc_row, loc_col] = 1

                    # Evaluate Move
                    new_board_to_play, new_moves_to_try = self.new_parameters(board, loc_row, loc_col)
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

                    # Simulate Move
                    row, col, loc_row, loc_col = move
                    local_to_play = board[row, col]
                    local_to_play[loc_row, loc_col] = -1

                    # Evaluate Move
                    new_board_to_play, new_moves_to_try = self.new_parameters(board, loc_row, loc_col)
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

    def new_parameters(self, board, loc_row, loc_col):
        ''' Given the local coords of a move to play, returns the new board_to_play and moves_to_try '''
        if self.get_over_hash(board[loc_row, loc_col]):
            board_to_play = None
            moves_to_try = self.generate_global_moves(board)
        else:
            board_to_play = (loc_row, loc_col)
            moves_to_try = np.argwhere(board[loc_row, loc_col] == 0)
        
        return board_to_play, moves_to_try

    def order_moves(self, board, moves_to_try):
        ''' Orders the moves on depth-0 '''
        # TODO: Complete this function to order moves, use moself.moveQuality
        # check that ordy.py uses it
        # then call it in Action to see if it's quicker or not
        # MAKE MONKEY PRINT HOW MUCH TIME IT TAKES TO RUN IT IN THE ACTION TO SEE IF ITS WORTH IT
        None

    def moveQuality(self, board, move, player=1):
        # FIXME This is not efficient, I think (idk)
        ''' Given a 4-coord move, returns the quality of the move by simulating it and retrieving balance '''
        board_copy = board.copy()
        original_balance = self.boardBalance(board_copy)
        r, c, r_l, c_l = move
        board_copy[r, c][r_l, c_l] = player
        new_balance = self.boardBalance(board_copy)
        return new_balance - original_balance

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
                if isEdge(r, c):
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

def canPlay(board, i, j):
    return board[i, j] == 0

def isEmpty(board):
    return np.count_nonzero(board) == 0

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
