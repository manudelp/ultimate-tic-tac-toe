import numpy as np

def test_generate_boards():
    # Limit the test to a few samples for checking correctness
    sample_states = [0, 1, 100, 5000, 262143]  # Choose a few states, including edge cases
    boards = []
    for state in sample_states:
        board = np.array([(state // 4**i) % 4 - 1 for i in range(9)]).reshape(3, 3)
        boards.append(board)
        print(f"State: {state}\nBoard:\n{board}\n")

test_generate_boards()
