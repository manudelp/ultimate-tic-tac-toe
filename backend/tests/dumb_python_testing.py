import numpy as np

def verify_format(board):
    row1 = [board[0, 0], board[0, 1], board[0, 2]]
    row2 = [board[1, 0], board[1, 1], board[1, 2]]
    row3 = [board[2, 0], board[2, 1], board[2, 2]]

    col1 = [board[0, 0], board[1, 0], board[2, 0]]
    col2 = [board[0, 1], board[1, 1], board[2, 1]]
    col3 = [board[0, 2], board[1, 2], board[2, 2]]

    diagTB = [board[0, 0], board[1, 1], board[2, 2]]
    diagBT = [board[2, 0], board[1, 1], board[0, 2]]

    if not np.array_equal(row1, board[0]):
        raise ValueError("Invalid Row 1")
    
    if not np.array_equal(row2, board[1]):
        raise ValueError("Invalid Row 2")
    
    if not np.array_equal(row3, board[2]):
        raise ValueError("Invalid Row 3")

    if not np.array_equal(col1, board[:, 0]):
        raise ValueError("Invalid Column 1")
    
    if not np.array_equal(col2, board[:, 1]):
        raise ValueError("Invalid Column 2")
    
    if not np.array_equal(col3, board[:, 2]):
        raise ValueError("Invalid Column 3")
    
for i in range(1_000_000):
    if i%200_000 == 0:
        print(f"Running test {i}")
    three_by_three_board = np.random.randint(0, 2, (3, 3))
    verify_format(three_by_three_board)

print("All tests passed!")