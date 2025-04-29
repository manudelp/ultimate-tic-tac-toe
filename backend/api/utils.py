"""
Re-exports of utility functions from the backend utils module.
This module acts as a bridge between the API and backend utilities.
"""
import os
import sys

# Import utils directly
# Since we're running from the backend directory, we can import utils directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils as backend_utils

# Re-export the functions
fancyBoardPrinter = backend_utils.fancyBoardPrinter
get_board_results = backend_utils.get_board_results
get_GlobalWinner = backend_utils.get_GlobalWinner
get_winner = backend_utils.get_winner

# Define __all__ for explicit exports
__all__ = [
    'fancyBoardPrinter',
    'get_board_results',
    'get_GlobalWinner',
    'get_winner'
]
