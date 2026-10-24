import numpy as np
from bots.base import BaseAgent
from core.board_utils import is_won, is_playable, can_play, random_move, safe_set_extractor
from core.rules import winning_cells


class GreedyAgent(BaseAgent):
    id = 1
    name = "Greedy"
    icon = "🤑"
    description = "Greedy is an agent that doesn't think much about the future, he just plays whatever looks best at first glance."

    def choose(self, position):
        super_board = position.mover_board()
        rows, cols = 3, 3
        board_to_play = position.forced_board

        # First Move Go Center
        if position.is_empty():
            return 1, 1, 1, 1

        if board_to_play is None:
            
            # Greedy Action! 
            
            # First Check Global Winner
            global_results = self.globalBoardResulter(super_board)
            global_winner = self.get_winnableByOne(global_results)
            if global_winner:
                for i in range(rows):
                    for j in range(cols):
                        if (i, j) in global_winner:
                            local_winnable = self.get_winnableByOne(super_board[i, j])
                            if is_playable(super_board[i, j]) and local_winnable:
                                local_row, local_col = safe_set_extractor(super_board, local_winnable)
                                return i, j, local_row, local_col
                        
            # Otherwise Check Wins
            for i in range(rows):
                for j in range(cols):
                    if is_playable(super_board[i, j]):
                        local_winner = self.get_winnableByOne(super_board[i, j])
                        if local_winner:
                            local_row, local_col = safe_set_extractor(super_board, local_winner)
                            return i, j, local_row, local_col
            
            # Otherwise, Check Blocks
            for i in range(rows):
                for j in range(cols):
                    if is_playable(super_board[i, j]):
                        local_blocker = self.get_winnableByMinusOne(super_board[i, j])
                        if local_blocker:
                            local_row, local_col = safe_set_extractor(super_board, local_blocker)
                            return i, j, local_row, local_col

            # Otherwise, Center Move
            if is_playable(super_board[1, 1]):
                row, col = 1, 1
                local_row, local_col = self.randomMove(super_board[row, col])
                return row, col, local_row, local_col

            # Otherwise, Random Move
            for i in range(rows):
                for j in range(cols):
                    if is_playable(super_board[i, j]):
                        local_row, local_col = self.randomMove(super_board[i, j])
                        return i, j, local_row, local_col
            
            raise ValueError(f"Greedy couldn't find a playable board!")
            
        else:
            a, b = board_to_play
            subboard = super_board[a, b]
            if not is_playable(subboard):
                raise ValueError(f"Greedy Board to play is not playable!")

        # Greedy Action
        local_winner = self.get_winnableByOne(subboard)
        local_blocker = self.get_winnableByMinusOne(subboard)
        
        # print(f"When btp is {board_to_play}, Local winner is {local_winner}, local blocker is {local_blocker}")
 
        # Win
        if local_winner:
            local_row, local_col = safe_set_extractor(super_board, local_winner)
        elif local_blocker:
            local_row, local_col = safe_set_extractor(super_board, local_blocker)
        elif can_play(subboard, a, b):
            local_row, local_col = a, b
        # Random
        else:
            local_row, local_col = self.randomMove(subboard)
            
        return a, b, local_row, local_col

    def randomMove(self, board):
        return random_move(board)

    def globalBoardResulter(self, super_board):
        results = np.zeros((3, 3), dtype=int)
        for i in range(3):
            for j in range(3):
                results[i, j] = is_won(super_board[i, j])
        return results

    def get_winnableByOne(self, board):
        ''' Returns the set of winning moves for player 1, if the board is winnable '''
        return winning_cells(board, 1)

    def get_winnableByMinusOne(self, board):
        ''' Returns the set of winning moves for player -1, if the board is winnable '''
        return winning_cells(board, -1)

