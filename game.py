ROWS = 6
COLS = 7
EMPTY = 0
PLAYER = 1  # Human
AI = 2      # Computer

def create_board():
    """Return an empty ROWS x COLS board (list of lists)."""
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

def valid_moves(board):
    """Return list of column indices that are not full."""
    return [c for c in range(COLS) if board[0][c] == EMPTY]

def make_move(board, col, player):
    """Drop a piece for `player` into `col`. Returns row where placed."""
    if col is None or col < 0 or col >= COLS:
        return None
    for r in range(ROWS-1, -1, -1):
        if board[r][col] == EMPTY:
            board[r][col] = player
            return r
    return None

def undo_move(board, col):
    """Remove the top-most disk from `col`."""
    for r in range(ROWS):
        if board[r][col] != EMPTY:
            board[r][col] = EMPTY
            return True
    return False

def is_full(board):
    """Return True if board is full."""
    return all(board[0][c] != EMPTY for c in range(COLS))

def check_winner(board, player):
    """Return True if `player` has 4 in a row."""
    # horizontal
    for r in range(ROWS):
        for c in range(COLS-3):
            if all(board[r][c+i] == player for i in range(4)):
                return True
    # vertical
    for c in range(COLS):
        for r in range(ROWS-3):
            if all(board[r+i][c] == player for i in range(4)):
                return True
    # diagonal '\'
    for r in range(ROWS-3):
        for c in range(COLS-3):
            if all(board[r+i][c+i] == player for i in range(4)):
                return True
    # diagonal '/'
    for r in range(3, ROWS):
        for c in range(COLS-3):
            if all(board[r-i][c+i] == player for i in range(4)):
                return True
    return False

def count_windows(board, player, length=4):
    """Count all windows of size `length` fully occupied by `player`."""
    cnt = 0
    # horizontal
    for r in range(ROWS):
        for c in range(COLS-length+1):
            if [board[r][c+i] for i in range(length)].count(player) == length:
                cnt += 1
    # vertical
    for c in range(COLS):
        for r in range(ROWS-length+1):
            if [board[r+i][c] for i in range(length)].count(player) == length:
                cnt += 1
    # diagonal '\'
    for r in range(ROWS-length+1):
        for c in range(COLS-length+1):
            if [board[r+i][c+i] for i in range(length)].count(player) == length:
                cnt += 1
    # diagonal '/'
    for r in range(length-1, ROWS):
        for c in range(COLS-length+1):
            if [board[r-i][c+i] for i in range(length)].count(player) == length:
                cnt += 1
    return cnt

def count_potentials(board, player):
    opp = PLAYER if player == AI else AI
    cnt = 0

    # horizontal
    for r in range(ROWS):
        for c in range(COLS-3):
            window = [board[r][c+i] for i in range(4)]
            if opp not in window and any(v == EMPTY for v in window):
                cnt += 1

    # vertical
    for c in range(COLS):
        for r in range(ROWS-3):
            window = [board[r+i][c] for i in range(4)]
            if opp not in window and any(v == EMPTY for v in window):
                cnt += 1

    # diagonal '\'
    for r in range(ROWS-3):
        for c in range(COLS-3):
            window = [board[r+i][c+i] for i in range(4)]
            if opp not in window and any(v == EMPTY for v in window):
                cnt += 1

    # diagonal '/'
    for r in range(3, ROWS):
        for c in range(COLS-3):
            window = [board[r-i][c+i] for i in range(4)]
            if opp not in window and any(v == EMPTY for v in window):
                cnt += 1

    return cnt
