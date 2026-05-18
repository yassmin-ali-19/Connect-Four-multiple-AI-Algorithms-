import pygame
import copy
from game import (
    ROWS, COLS, EMPTY, PLAYER, AI,
    create_board, valid_moves, make_move, is_full
)
from ai import (
    choose_move_minimax, choose_move_alphabeta, choose_move_expected,
    heuristic, tree_nodes
)

pygame.init()

# Screen
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
FPS = 60

# Colors
BG_COLOR = (15, 20, 35)
BOARD_COLOR = (25, 35, 60)
FRAME_COLOR = (200, 170, 100)
HIGHLIGHT_COLOR = (100, 200, 255)
TEXT_COLOR = (240, 240, 250)

CELL_SIZE = 80
BOARD_X = (SCREEN_WIDTH - COLS * CELL_SIZE) // 2
BOARD_Y = 120
PIECE_RADIUS = CELL_SIZE // 2 - 8

# AI Algorithms
AI_ALGOS = ["Minimax", "AlphaBeta", "ExpectedMinimax"]

class ConnectFourGUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Connect Four")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 60)
        self.font_medium = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 28)

        # Color selection
        self.color_selection_active = True
        self.player_color = None
        self.ai_color = None
        self.color_options = [
            {"name": "Yellow", "player": (255, 200, 80), "ai": (220, 50, 90)},
            {"name": "Cyan", "player": (100, 200, 255), "ai": (220, 50, 90)},
            {"name": "Green", "player": (100, 255, 150), "ai": (220, 50, 90)},
            {"name": "Purple", "player": (200, 100, 255), "ai": (220, 50, 90)},
        ]
        self.selected_color_index = 0
        self.color_button_rects = []

        # K selection
        self.k_selection_active = False
        self.K_value = 4

        # AI selection
        self.ai_selection_active = False
        self.selected_ai_index = 0

        # Game state
        self.board = create_board()
        self.game_over = False
        self.final_score_displayed = False
        self.human_turn = True
        self.ai_algorithm = "AlphaBeta"

        # Hover
        self.hover_col = None

    # -------------------
    # Color Selection Menu
    # -------------------
    def draw_color_selection(self):
        self.screen.fill(BG_COLOR)
        title = self.font_large.render("Choose Your Color", True, FRAME_COLOR)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 80)))

        self.color_button_rects = []
        button_width = 120
        button_height = 120
        total_width = len(self.color_options) * button_width + (len(self.color_options)-1)*30
        start_x = (SCREEN_WIDTH - total_width)//2
        button_y = 300

        for i, color_opt in enumerate(self.color_options):
            x = start_x + i*(button_width + 30)
            rect = pygame.Rect(x, button_y, button_width, button_height)
            self.color_button_rects.append(rect)
            selected = i == self.selected_color_index
            pygame.draw.rect(self.screen, FRAME_COLOR if selected else (80,100,130), rect, 5 if selected else 2, border_radius=10)
            pygame.draw.circle(self.screen, color_opt["player"], (x+button_width//2, button_y+40), 25)
            name_surf = self.font_small.render(color_opt["name"], True, TEXT_COLOR)
            self.screen.blit(name_surf, name_surf.get_rect(center=(x+button_width//2, button_y+85)))

        instr = self.font_small.render("Use Arrows and ENTER or click to select", True, HIGHLIGHT_COLOR)
        self.screen.blit(instr, instr.get_rect(center=(SCREEN_WIDTH//2, 550)))
        pygame.display.flip()

    def handle_color_selection_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.selected_color_index = (self.selected_color_index -1) % len(self.color_options)
                elif event.key == pygame.K_RIGHT:
                    self.selected_color_index = (self.selected_color_index +1) % len(self.color_options)
                elif event.key == pygame.K_RETURN:
                    self.confirm_color_selection()
                    return True
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for i, rect in enumerate(self.color_button_rects):
                    if rect.collidepoint(pos):
                        self.selected_color_index = i
                        self.confirm_color_selection()
                        return True
        return True

    def confirm_color_selection(self):
        sel = self.color_options[self.selected_color_index]
        self.player_color = sel["player"]
        self.ai_color = sel["ai"]
        self.color_selection_active = False
        self.k_selection_active = True

    # -------------------
    # K Selection Menu
    # -------------------
    def draw_k_selection(self):
        self.screen.fill(BG_COLOR)
        title = self.font_large.render("Choose Search Depth (K)", True, FRAME_COLOR)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 80)))

        surf = self.font_medium.render(f"Current K = {self.K_value}", True, HIGHLIGHT_COLOR)
        self.screen.blit(surf, surf.get_rect(center=(SCREEN_WIDTH//2, 250)))

        instr = self.font_small.render("Use UP/DOWN to change, ENTER to confirm", True, TEXT_COLOR)
        self.screen.blit(instr, instr.get_rect(center=(SCREEN_WIDTH//2, 500)))
        pygame.display.flip()

    def handle_k_selection_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.K_value += 1
                elif event.key == pygame.K_DOWN:
                    if self.K_value > 1:
                        self.K_value -= 1
                elif event.key == pygame.K_RETURN:
                    import ai
                    ai.K = self.K_value
                    self.k_selection_active = False
                    self.ai_selection_active = True
        return True

    # -------------------
    # AI Algorithm Selection
    # -------------------
    def draw_ai_selection(self):
        self.screen.fill(BG_COLOR)
        title = self.font_large.render("Choose AI Algorithm", True, FRAME_COLOR)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 80)))

        for i, algo in enumerate(AI_ALGOS):
            color = HIGHLIGHT_COLOR if i==self.selected_ai_index else TEXT_COLOR
            surf = self.font_medium.render(algo, True, color)
            self.screen.blit(surf, surf.get_rect(center=(SCREEN_WIDTH//2, 250 + i*60)))

        instr = self.font_small.render("Use Arrows and ENTER to select AI", True, HIGHLIGHT_COLOR)
        self.screen.blit(instr, instr.get_rect(center=(SCREEN_WIDTH//2, 500)))
        pygame.display.flip()

    def handle_ai_selection_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # return False
                pass
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_ai_index = (self.selected_ai_index -1) % len(AI_ALGOS)
                elif event.key == pygame.K_DOWN:
                    self.selected_ai_index = (self.selected_ai_index +1) % len(AI_ALGOS)
                elif event.key == pygame.K_RETURN:
                    self.ai_algorithm = AI_ALGOS[self.selected_ai_index]
                    self.ai_selection_active = False
        return True

    # -------------------
    # Board & Pieces
    # -------------------
    def draw_board(self):
        frame_rect = pygame.Rect(BOARD_X-15, BOARD_Y-15, COLS*CELL_SIZE+30, ROWS*CELL_SIZE+30)
        pygame.draw.rect(self.screen, FRAME_COLOR, frame_rect, 8, border_radius=15)
        board_rect = pygame.Rect(BOARD_X, BOARD_Y, COLS*CELL_SIZE, ROWS*CELL_SIZE)
        pygame.draw.rect(self.screen, BOARD_COLOR, board_rect, border_radius=10)
        for r in range(ROWS):
            for c in range(COLS):
                x = BOARD_X + c*CELL_SIZE + CELL_SIZE//2
                y = BOARD_Y + r*CELL_SIZE + CELL_SIZE//2
                pygame.draw.circle(self.screen, (35,50,80), (x,y), PIECE_RADIUS, 2)

    def draw_pieces(self):
        for r in range(ROWS):
            for c in range(COLS):
                if self.board[r][c] != EMPTY:
                    color = self.player_color if self.board[r][c]==PLAYER else self.ai_color
                    x = BOARD_X + c*CELL_SIZE + CELL_SIZE//2
                    y = BOARD_Y + r*CELL_SIZE + CELL_SIZE//2
                    pygame.draw.circle(self.screen, color, (x,y), PIECE_RADIUS)
                    pygame.draw.circle(self.screen, (0,0,0), (x,y), PIECE_RADIUS, 2)

    def draw_ui(self):
        title_surf = self.font_large.render("CONNECT FOUR", True, FRAME_COLOR)
        self.screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH//2, 40)))
        if self.hover_col is not None and self.human_turn:
            x = BOARD_X + self.hover_col*CELL_SIZE + CELL_SIZE//2
            pygame.draw.circle(self.screen, HIGHLIGHT_COLOR, (x, BOARD_Y-30), 15)

        status_y = BOARD_Y + ROWS*CELL_SIZE + 30
        if self.game_over and self.final_score_displayed:
            status_text = f"Final Score - You: {self.player_score} | AI: {self.ai_score}"
        else:
            status_text = "Your Turn" if self.human_turn else "AI is thinking..."
        status_surf = self.font_medium.render(status_text, True, HIGHLIGHT_COLOR)
        self.screen.blit(status_surf, status_surf.get_rect(center=(SCREEN_WIDTH//2, status_y)))

    # -------------------
    # Bonus: Tree Visualization Panel
    # -------------------
    def draw_tree_panel(self):
        panel_x = 50
        panel_y = BOARD_Y + ROWS*CELL_SIZE + 80
        node_radius = 20
        y_spacing = 70
        x_spacing = 120

        for (depth, col, score, maximizing) in tree_nodes:
            # Only best path are recorded
            try:
                col_val = int(col)
            except (TypeError, ValueError):
                col_val = 0

            x = panel_x + col_val * 40
            y = panel_y + depth * y_spacing
            color = (100,200,255) if maximizing else (220,50,90)

            pygame.draw.circle(self.screen, color, (x,y), node_radius)
            label = f"{col}:{score}"
            surf = self.font_small.render(label, True, TEXT_COLOR)
            self.screen.blit(surf, surf.get_rect(center=(x,y)))


    # -------------------
    # Input & Moves
    # -------------------
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEMOTION:
                x = event.pos[0]
                if BOARD_X <= x < BOARD_X+COLS*CELL_SIZE:
                    self.hover_col = (x-BOARD_X)//CELL_SIZE
                else:
                    self.hover_col = None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.game_over and self.human_turn:
                    col = self.hover_col
                    if col in valid_moves(self.board):
                        make_move(self.board, col, PLAYER)
                        self.human_turn = False
        return True

    # -------------------
    # AI Move
    # -------------------
    def ai_move_step(self):
        if not self.human_turn and not self.game_over:
            import ai
            ai.tree_nodes.clear()
            print("\n--- AI Thinking ---")
            print(f"AI Algorithm: {self.ai_algorithm} | K={self.K_value}")
            if self.ai_algorithm == "Minimax":
                col = choose_move_minimax(self.board, depth=self.K_value)
            elif self.ai_algorithm == "AlphaBeta":
                col = choose_move_alphabeta(self.board, depth=self.K_value)
            else:
                col = choose_move_expected(self.board, depth=self.K_value)
            print(f"AI chooses column: {col}\n")
            if col in valid_moves(self.board):
                make_move(self.board, col, AI)
            self.human_turn = True

    # -------------------
    # Scoring & Game Over
    # -------------------
    def check_final_score(self):
        def count_player_score(player):
            count = 0
            # horizontal
            for r in range(ROWS):
                for c in range(COLS-3):
                    if all(self.board[r][c+i]==player for i in range(4)):
                        count +=1
            # vertical
            for c in range(COLS):
                for r in range(ROWS-3):
                    if all(self.board[r+i][c]==player for i in range(4)):
                        count +=1
            # diag \
            for r in range(ROWS-3):
                for c in range(COLS-3):
                    if all(self.board[r+i][c+i]==player for i in range(4)):
                        count +=1
            # diag /
            for r in range(3, ROWS):
                for c in range(COLS-3):
                    if all(self.board[r-i][c+i]==player for i in range(4)):
                        count +=1
            return count

        self.player_score = count_player_score(PLAYER)
        self.ai_score = count_player_score(AI)
        self.final_score_displayed = True
        self.game_over = True

    # -------------------
    # Draw & Run
    # -------------------
    def draw(self):
        self.screen.fill(BG_COLOR)
        self.draw_board()
        self.draw_pieces()
        self.draw_ui()
        self.draw_tree_panel()  
        pygame.display.flip()

    def run(self):
        running = True

        while self.color_selection_active and running:
            running = self.handle_color_selection_input()
            self.draw_color_selection()

        while self.k_selection_active and running:
            running = self.handle_k_selection_input()
            self.draw_k_selection()

        while self.ai_selection_active and running:
            running = self.handle_ai_selection_input()
            self.draw_ai_selection()

        while running:
            running = self.handle_input()
            if not self.human_turn and not self.game_over:
                self.ai_move_step()
            if not self.game_over and is_full(self.board):
                self.check_final_score()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()

if __name__ == "__main__":
    gui = ConnectFourGUI()
    gui.run()