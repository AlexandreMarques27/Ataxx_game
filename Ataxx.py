import pygame
from pygame.locals import QUIT, MOUSEBUTTONDOWN
from pygame import time


class Ataxx:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.board = self.create_board()
        self.turn = 1

    def copy(self):
        new_state = Ataxx(self.rows, self.cols)
        new_state.board = [row[:] for row in self.board]
        new_state.turn = self.turn
        return new_state

    def create_board(self):
        board = []
        for i in range(self.rows):
            board.append([0] * self.cols)
        board[0][0] = board[self.rows-1][self.cols-1] = -1
        board[self.rows-1][0] = board[0][self.cols-1] = 1
        return board

    def is_clear(self, i, j):
        return 0 <= i < self.rows and 0 <= j < self.cols and self.board[i][j] == 0

    def sucessors_jump(self, i, j):
        sucessors = []
        for n in range(-2, 3):
            for m in range(-2, 3):
                if self.is_clear(i+n, j+m) and (abs(n) == 2 or abs(m) == 2):
                    sucessors.append((i+n, j+m))
        return sucessors

    def sucessors_walk(self, i, j):
        sucessors = []
        for n in range(-1, 2):
            for m in range(-1, 2):
                if self.is_clear(i+n, j+m):
                    sucessors.append((i+n, j+m))
        return sucessors

    def get_player_pieces(self, player):
        pieces = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] == player:
                    pieces.append((i, j))
        return pieces

    def get_legal_moves(self, player):
        j = []
        w = []
        for piece in self.get_player_pieces(player):
            j.extend((piece, s) for s in self.sucessors_jump(piece[0], piece[1]))
            w.extend((piece, s) for s in self.sucessors_walk(piece[0], piece[1]))
        moves = w, j
        return moves

    def capture_adjacents(self, i, j, player):
        for n in range(-1, 2):
            for m in range(-1, 2):
                if 0 <= i+n < self.rows and 0 <= j+m < self.cols and self.board[i+n][j+m] == -player:
                    self.board[i+n][j+m] = player

    def make_move(self, piece, move, player):
        w, j = self.get_legal_moves(player)
        w = [w[1] for w in w if w[0] == piece]
        j = [j[1] for j in j if j[0] == piece]
        if move in w:
            self.board[move[0]][move[1]] = player
            self.capture_adjacents(move[0], move[1], player)
            return True
        elif move in j:
            self.board[move[0]][move[1]] = player
            self.board[piece[0]][piece[1]] = 0
            self.capture_adjacents(move[0], move[1], player)
            return True
        return False

    def change_turn(self):
        self.turn *= -1

    def fill_board(self, player):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] == 0:
                    self.board[i][j] = player

    def get_winner(self):
        pieces1 = 0
        pieces2 = 0
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] == 1:
                    pieces1 += 1
                elif self.board[i][j] == -1:
                    pieces2 += 1
        if pieces1 > pieces2:
            return 1
        elif pieces2 > pieces1:
            return -1
        else:
            return 2

    def full_board(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] == 0:
                    return False
        return True

    def game_over(self):
        pieces1 = self.get_player_pieces(1)
        pieces2 = self.get_player_pieces(-1)
        moves1 = self.get_legal_moves(1)
        moves2 = self.get_legal_moves(-1)
        if self.full_board():
            w = self.get_winner()
            return w
        elif len(pieces1) == 0:
            return -1
        elif len(pieces2) == 0:
            return 1
        elif len(moves1) == 0:
            self.fill_board(-1)
            w = self.get_winner()
            return w
        elif len(moves2) == 0:
            self.fill_board(1)
            w = self.get_winner()
            return w
        return 0

    def show_winner(self, screen, winner):
        font = pygame.font.Font(None, 30)
        if winner != 2:
            color = 'blue' if winner == 1 else 'green'
            text = font.render(f"Game Over, {color} wins", True, (255, 255, 255))
        else:
            text = font.render("Game Over, it's a tie", True, (255, 255, 255))
        text_rect = text.get_rect(center=((self.rows * 100) / 2, (self.cols * 100) / 2))
        screen.blit(text, text_rect)
        pygame.display.flip()

    def heuristic(self, player):
        pieces1 = 0
        pieces2 = 0
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] == 1:
                    pieces1 += 1
                elif self.board[i][j] == -1:
                    pieces2 += 1
        if player == 1:
            return pieces1
        return pieces2

    def generate_successors(self, state, player):
        successors = []
        cols = []
        for piece in state.get_player_pieces(player):
            for move in state.sucessors_jump(piece[0], piece[1]):
                new_state = state.copy()
                new_state.make_move(piece, move, player)
                successors.append(new_state)
                cols.append((piece, move))
            for move in state.sucessors_walk(piece[0], piece[1]):
                new_state = state.copy()
                new_state.make_move(piece, move, player)
                successors.append(new_state)
                cols.append((piece, move))
        return successors, cols

    def minimax(self, state, depth, maximizing_player):

        if depth == 0 or state.game_over() != 0:
            if state.game_over() != 0:
                if state.game_over() == 1:
                    return None, -512
                elif state.game_over() == -1:
                    return None, 512
                else:
                    return None, 0
            else:
                return None, abs(state.heuristic(-1))  # ???
        if maximizing_player:
            col = None
            value = float('-inf')
            successors, cols = self.generate_successors(state, -1)
            for i, child in enumerate(successors):
                _, child_value = self.minimax(child, depth - 1, False)
                value, col = max((value, col), (child_value, cols[i]))
            return col, value
        else:
            col = None
            value = float('inf')
            successors, cols = self.generate_successors(state, 1)
            for i, child in enumerate(successors):
                _, child_value = self.minimax(child, depth - 1, True)
                value, col = min((value, col), (child_value, cols[i]))
            return col, value

    def play_game(self):
        pygame.init()
        pygame.font.init()

        screen_width = self.rows * 100
        screen_height = self.cols * 100
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.flip()

        pygame.display.set_caption("Ataxx")
        clock = pygame.time.Clock()
        interface = Interface()
        selected_piece = None
        while self.game_over() == 0:
            if self.turn == -1:
                col, value = self.minimax(self, 3, True)
                self.make_move(col[0], col[1], self.turn)
                self.change_turn()
                interface.draw_board(screen, game, self.board, selected_piece)
                continue
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    quit()
                elif event.type == MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    col = mouse_pos[0] // 100
                    row = mouse_pos[1] // 100
                    if 0 <= row < self.rows and 0 <= col < self.cols:
                        if selected_piece is None:
                            if game.board[row][col] == game.turn:
                                selected_piece = (row, col)

                        elif selected_piece == (row, col):
                            selected_piece = None

                        else:
                            legal_actions = self.get_legal_moves(self.turn)
                            w, j = legal_actions
                            moves = [w[1] for w in w if w[0] == selected_piece]
                            moves.extend([j[1] for j in j if j[0] == selected_piece])
                            if (row, col) in moves:
                                self.make_move(selected_piece, (row, col), self.turn)
                                selected_piece = None
                                self.change_turn()
                                break
            interface.draw_board(screen, game, self.board, selected_piece)
            pygame.display.flip()
            clock.tick(30)  # Adjust the frame rate as needed
        winner = self.game_over()
        self.show_winner(screen, winner)
        pygame.time.wait(1000)


class Interface:
    def draw_board(self, screen, game, board, selected_piece=None):
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        GRAY = (150, 150, 150)
        BLUE = (0, 0, 255)
        DARK_BLUE = (0, 0, 150)
        GREEN = (0, 255, 0)
        DARK_GREEN = (0, 150, 0)
        rows, cols = game.rows, game.cols
        offset = (screen.get_width() - cols * 100) // 2

        screen.fill(WHITE)

        for row in range(rows):
            for col in range(cols):
                x = col * 100 + 50 + offset
                y = row * 100 + 50 + offset

                # Draw the board circles
                pygame.draw.circle(screen, BLACK, (x, y), 40)

                # Draw pieces
                if board[row][col] == 1:
                    pygame.draw.circle(screen, BLUE, (x, y), 40)
                elif board[row][col] == -1:
                    pygame.draw.circle(screen, GREEN, (x, y), 40)

                # Highlight selected piece
                if (row, col) == selected_piece:
                    if game.turn == 1:
                        pygame.draw.circle(screen, DARK_BLUE, (x, y), 40)
                    else:
                        pygame.draw.circle(screen, DARK_GREEN, (x, y), 40)

                # Highlight possible moves for walkers and jumpers of the selected piece
                if selected_piece is not None:
                    walkers, jumpers = game.get_legal_moves(game.turn)

                    if (selected_piece, (row, col)) in walkers:
                        pygame.draw.circle(screen, GRAY, (x, y), 40)

                    if (selected_piece, (row, col)) in jumpers:
                        pygame.draw.circle(screen, GRAY, (x, y), 40)

        pygame.display.flip()


game = Ataxx(7, 7)
game.play_game()
