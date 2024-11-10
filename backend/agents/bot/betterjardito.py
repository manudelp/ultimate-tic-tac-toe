import numpy as np
import random
import os
import time
from colorama import init, Fore, Style

"""
depth = 6/5, plain alpha beta
Board Balance = Sum of Local Board Balances
AB-Pruning Minimax? = True
Order Moves? = False!

"""

class JardineritoAgent:
    def __init__(self):
        self.id = "Jaimito el Euristico"
        self.icon = "🍀"
        self.moveNumber = 0
        self.depth_local = 6 # when btp is not None
        self.depth_global = 5 # when btp is None
        self.time_limit = 10 # in seconds
        self.total_minimax_time = 0
        self.minimax_plays = 0
        self.hash_over_boards = {}
        self.hash_eval_boards = {}

        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # Construct the absolute paths to the files
        over_boards_path = os.path.join(root_dir, 'agents', 'hashes', 'hash_over_boards.txt')
        evaluated_boards_path = os.path.join(root_dir, 'agents', 'hashes', 'hash_evaluated_boards.txt')

        # Load the boards using the absolute paths
        self.load_over_boards(over_boards_path)
        self.load_evaluated_boards(evaluated_boards_path)

        self.over_boards_set = set()
        self.model_over_boards_set = set()
        self.playable_boards_set = set()
        self.model_playable_boards_set = set() 
    
    def __str__(self):
        self.str = f"{self.id}{self.icon}"
        return self.str

