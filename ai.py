import time
from game import (
    ROWS, COLS, PLAYER, AI,EMPTY,
    valid_moves, make_move, undo_move,
    count_windows, count_potentials
)

# Global cutoff depth (set by GUI)
K = 4

# Performance metrics and logging
nodes_expanded = 0
verbose = True  # toggle console printing
tree_nodes = []  # for tree visualization

def reset_metrics():
    global nodes_expanded, tree_nodes
    nodes_expanded = 0
    tree_nodes.clear()

def print_metrics(elapsed_sec, algo_name):
    print(f"[{algo_name}] Nodes expanded: {nodes_expanded} | Time: {elapsed_sec:.3f}s\n")

def record_node(depth, col, score, maximizing, best=False):
    """
    Store node info for GUI tree.
    Only keep best path nodes.
    """
    if depth <= 2 or best:  # limit depth
        tree_nodes.append((depth, col, score, maximizing))


# -----------------------------
# Heuristic function
# -----------------------------
def heuristic(board):
    score = 0
    center_col = [row[COLS // 2] for row in board]
    score += center_col.count(AI) * 3

    score += count_windows(board, AI, 2) * 2
    score += count_windows(board, AI, 3) * 6
    score += count_windows(board, AI, 4) * 100

    score -= count_windows(board, PLAYER, 2) * 2
    score -= count_windows(board, PLAYER, 3) * 8
    score -= count_windows(board, PLAYER, 4) * 120

    score += count_potentials(board, AI)
    score -= count_potentials(board, PLAYER)

    return score

# -------------------------
# Move ordering
# -------------------------
def ordered_moves(board):
    moves = valid_moves(board)
    center = COLS // 2
    moves.sort(key=lambda c: abs(center - c))
    return moves

# -----------------------
# Tree printing helpers
# -----------------------
def print_node(prefix, depth, col, score, maximizing, is_last=False):
    if not verbose or depth > 3:
        return
    player = "AI" if maximizing else "PLAYER"
    move_str = f"col={col}" if col is not None else "leaf"
    connector = "└──" if is_last else "├──"
    line = f"{prefix}{connector} [{player}] {move_str} h={score}"
    print(line)
    record_node(depth, col, score, maximizing,True)

def print_expected_child(prefix, depth, intent_col, outcome_col, p_norm, child_val, maximizing):
    if not verbose or depth > 2:
        return
    who = "AI" if maximizing else "PLAYER"
    line = (f"{prefix}{'  ' * depth}[{who}] intent={intent_col} -> "
            f"outcome={outcome_col} p={p_norm:.2f} h={child_val}")
    print(line)
    record_node(depth, outcome_col, child_val, maximizing,True)

# -----------------------
# Minimax
# -----------------------
def minimax(board, depth, maximizing, prefix=""):
    global nodes_expanded
    nodes_expanded += 1
    moves = ordered_moves(board)
    if depth == 0 or not moves:
        score = heuristic(board)
        print_node(prefix, 0, None, score, maximizing, True)
        return score, None

    if maximizing:
        max_eval = -float('inf')
        best_col = moves[0]
        for i, col in enumerate(moves):
            make_move(board, col, AI)
            val, _ = minimax(board, depth - 1, False, prefix + "  ")
            undo_move(board, col)
            print_node(prefix, depth, col, val, True, i == len(moves)-1)
            if val > max_eval:
                max_eval = val
                best_col = col
        return max_eval, best_col
    else:
        min_eval = float('inf')
        best_col = moves[0]
        for i, col in enumerate(moves):
            make_move(board, col, PLAYER)
            val, _ = minimax(board, depth - 1, True, prefix + "  ")
            undo_move(board, col)
            print_node(prefix, depth, col, val, False, i == len(moves)-1)
            if val < min_eval:
                min_eval = val
                best_col = col
        return min_eval, best_col

# ----------------------------
# Alpha-Beta
# ----------------------------
def minimax_ab(board, depth, alpha=-float('inf'), beta=float('inf'), maximizing=True, prefix=""):
    global nodes_expanded
    nodes_expanded += 1
    moves = ordered_moves(board)
    if depth == 0 or not moves:
        score = heuristic(board)
        print_node(prefix, 0, None, score, maximizing, True)
        return score, None

    if maximizing:
        max_eval = -float('inf')
        best_col = moves[0]
        for i, col in enumerate(moves):
            make_move(board, col, AI)
            val, _ = minimax_ab(board, depth - 1, alpha, beta, False, prefix + "  ")
            undo_move(board, col)
            print_node(prefix, depth, col, val, True, i == len(moves)-1)
            if val > max_eval:
                max_eval = val
                best_col = col
            alpha = max(alpha, max_eval)
            if alpha >= beta:
                break
        return max_eval, best_col
    else:
        min_eval = float('inf')
        best_col = moves[0]
        for i, col in enumerate(moves):
            make_move(board, col, PLAYER)
            val, _ = minimax_ab(board, depth - 1, alpha, beta, True, prefix + "  ")
            undo_move(board, col)
            print_node(prefix, depth, col, val, False, i == len(moves)-1)
            if val < min_eval:
                min_eval = val
                best_col = col
            beta = min(beta, min_eval)
            if alpha >= beta:
                break
        return min_eval, best_col

# --------------------------------------
# Expected Minimax
# --------------------------------------
def expected_minimax(board, depth, maximizing=True, prefix=""):
    global nodes_expanded
    nodes_expanded += 1
    moves = ordered_moves(board)
    if depth == 0 or not moves:
        score = heuristic(board)
        print_node(prefix, 0, None, score, maximizing, True)
        return score, None

    best_intent_val = -float('inf') if maximizing else float('inf')
    best_col = moves[0]

    for intent_col in moves:
        outcomes = []
        if intent_col in valid_moves(board):
            outcomes.append((intent_col, 0.6))
        left_col = intent_col - 1 if intent_col - 1 >= 0 else None
        right_col = intent_col + 1 if intent_col + 1 < COLS else None
        left_valid = left_col is not None and (board[0][left_col] == EMPTY)
        right_valid = right_col is not None and (board[0][right_col] == EMPTY)
        if left_valid and right_valid:
            outcomes.append((left_col, 0.2))
            outcomes.append((right_col, 0.2))
        elif left_valid:
            outcomes.append((left_col, 0.4))
        elif right_valid:
            outcomes.append((right_col, 0.4))
        if not outcomes:
            vm = valid_moves(board)
            if not vm:
                leaf_score = heuristic(board)
                print_node(prefix, 0, None, leaf_score, maximizing, True)
                return leaf_score, None
            p_uniform = 1.0 / len(vm)
            outcomes = [(c, p_uniform) for c in vm]

        total_p = sum(p for _, p in outcomes)
        expected_val = 0.0
        for oc, p in outcomes:
            if oc not in valid_moves(board):
                continue
            make_move(board, oc, AI if maximizing else PLAYER)
            child_val, _ = expected_minimax(board, depth - 1, not maximizing, prefix + "  ")
            undo_move(board, oc)
            p_norm = p / total_p if total_p > 0 else 0.0
            expected_val += p_norm * child_val
            print_expected_child(prefix, depth, intent_col, oc, p_norm, child_val, maximizing)

        if maximizing and expected_val > best_intent_val:
            best_intent_val = expected_val
            best_col = intent_col
        elif not maximizing and expected_val < best_intent_val:
            best_intent_val = expected_val
            best_col = intent_col

    print_node(prefix, depth, f"intent:{best_col}", best_intent_val, maximizing, True)
    return best_intent_val, best_col

# --------------------
# Wrappers
# --------------------
def choose_move_minimax(board, depth=None):
    d = depth if depth else K
    reset_metrics()
    start = time.time()
    val, col = minimax(board, d, True)
    elapsed = time.time() - start
    print_metrics(elapsed, "Minimax")
    return col

def choose_move_alphabeta(board, depth=None):
    d = depth if depth else K
    reset_metrics()
    start = time.time()
    val, col = minimax_ab(board, d, -float('inf'), float('inf'), True)
    elapsed = time.time() - start
    print_metrics(elapsed, "AlphaBeta")
    return col

def choose_move_expected(board, depth=None):
    d = depth if depth else K
    reset_metrics()
    start = time.time()
    val, col = expected_minimax(board, d, True)
    elapsed = time.time() - start
    print_metrics(elapsed, "ExpectedMinimax")
    return col
