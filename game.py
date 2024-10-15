import pygame as pg
import sys

pg.init()
pg.display.set_caption('Army Chess')

MIN_WIDTH, MIN_HEIGHT = 640, 480
screen = pg.display.set_mode((1280, 720), pg.RESIZABLE)
SQUARE_SIZE = int(screen.get_height() * 0.8) // 8

WHITE, BLACK = (255, 255, 255), (0, 0, 0)
LIGHT_BROWN = (220, 185, 140)
DARK_BROWN = (120, 60, 40)
board = [
    ['b_rook', 'b_knight', 'b_bishop', 'b_queen', 'b_king', 'b_bishop', 'b_knight', 'b_rook'],
    ['b_pawn'] * 8,
    ['--'] * 8,
    ['--'] * 8,
    ['--'] * 8,
    ['--'] * 8,
    ['w_pawn'] * 8,
    ['w_rook', 'w_knight', 'w_bishop', 'w_queen', 'w_king', 'w_bishop', 'w_knight', 'w_rook']
]

def load_image(name):
    try:
        image = pg.image.load(f'images/{name}.png').convert_alpha()
        return image
    except pg.error as e:
        print(f"Unable to load image {name}.png: {e}")
        return pg.Surface((SQUARE_SIZE, SQUARE_SIZE))  # Placeholder surface
original_pieces = {
    
    'b_king': load_image('b_king'),
    'b_queen': load_image('b_queen'),
    'b_rook': load_image('b_rook'),
    'b_bishop': load_image('b_bishop'),
    'b_knight': load_image('b_knight'),
    'b_pawn': load_image('b_pawn'),
    'w_king': load_image('w_king'),
    'w_queen': load_image('w_queen'),
    'w_rook': load_image('w_rook'),
    'w_bishop': load_image('w_bishop'),
    'w_knight': load_image('w_knight'),
    'w_pawn': load_image('w_pawn'),
}
pieces = original_pieces.copy()
background = pg.transform.smoothscale(pg.image.load('images/woodbackground.jpeg'), (screen.get_width(), screen.get_height()))
current_player = 'w'
font = pg.font.SysFont(None, 36)


# Resize pieces to fit squares
BOARD_MARGIN = int(screen.get_height() * 0.1)
def resize_pieces():
    global SQUARE_SIZE, pieces
    SQUARE_SIZE = (min(screen.get_width(), screen.get_height()) - int(screen.get_height() * 0.1) * 2) // 8
    for key in pieces:
        pieces[key] = pg.transform.smoothscale(original_pieces[key], (SQUARE_SIZE, SQUARE_SIZE))

resize_pieces()

# Draw the chessboard
def draw_board():
    # Draw the background
    screen.blit(background, (0, 0))
    
    # Draw the chessboard centered on the background with a margin
    board_width = 8 * SQUARE_SIZE
    board_height = 8 * SQUARE_SIZE
    board_x = (screen.get_width() - board_width) // 2
    board_y = (screen.get_height() - board_height) // 2
    colors = [LIGHT_BROWN, DARK_BROWN]
    
    # Draw black border
    border_width = SQUARE_SIZE // 8
    border_rect = pg.Rect(board_x - border_width, board_y - border_width, board_width + 2 * border_width, board_height + 2 * border_width)
    pg.draw.rect(screen, BLACK, border_rect)
    
    # Draw squares
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            rect = pg.Rect(board_x + col * SQUARE_SIZE, board_y + row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pg.draw.rect(screen, color, rect)
            # Highlight selected piece
            if selected_position == (row, col):
                pg.draw.rect(screen, (255, 255, 0, 50), rect, 3)  # Yellow border
# Draw pieces on the board
def draw_pieces(board):
    board_width = 8 * SQUARE_SIZE
    board_height = 8 * SQUARE_SIZE
    board_x = (screen.get_width() - board_width) // 2
    board_y = (screen.get_height() - board_height) // 2
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece != '--':
                screen.blit(pieces[piece], (board_x + col * SQUARE_SIZE, board_y + row * SQUARE_SIZE))


def is_in_check(player_color, board):
    # Find the king's position
    king_position = None
    for row in range(8):
        for col in range(8):
            if board[row][col] == f'{player_color}_king':
                king_position = (row, col)
                break
        if king_position:
            break
    if king_position is None:
        # King not found; game over
        return False

    # Check if any opponent's piece can move to the king's position
    opponent_color = 'b' if player_color == 'w' else 'w'
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece.startswith(opponent_color):
                if is_valid_move(piece, (row, col), king_position, board, check_check=False):
                    return True
    return False


selected_piece = None
selected_position = None
def is_valid_move(piece, start, end, board, check_check=True):
    if start == end:
        return False
    start_row, start_col = start
    end_row, end_col = end
    piece_type = piece[2:]
    piece_color = piece[0]
    target_piece = board[end_row][end_col]

    # Prevent moving onto a piece of the same color
    if target_piece != '--' and target_piece[0] == piece_color:
        return False

    valid = False  # Initialize the valid flag to False

    # Movement logic for different pieces
    if piece_type == 'pawn':
        direction = -1 if piece_color == 'w' else 1
        # Normal move
        if start_col == end_col and board[end_row][end_col] == '--':
            if end_row == start_row + direction:
                valid = True
            # Double move on first turn
            elif (start_row == 1 and piece_color == 'b') or (start_row == 6 and piece_color == 'w'):
                if end_row == start_row + 2 * direction and board[start_row + direction][start_col] == '--':
                    valid = True
        # Capture move
        elif abs(start_col - end_col) == 1 and end_row == start_row + direction and target_piece != '--':
            valid = True

    elif piece_type == 'rook':
        if start_row == end_row or start_col == end_col:
            step_row = 0 if start_row == end_row else (1 if end_row > start_row else -1)
            step_col = 0 if start_col == end_col else (1 if end_col > start_col else -1)
            current_row, current_col = start_row + step_row, start_col + step_col
            valid = True
            while current_row != end_row or current_col != end_col:
                if board[current_row][current_col] != '--':
                    valid = False
                    break
                current_row += step_row
                current_col += step_col

    elif piece_type == 'knight':
        if (abs(start_row - end_row), abs(start_col - end_col)) in [(2, 1), (1, 2)]:
            valid = True

    elif piece_type == 'bishop':
        if abs(start_row - end_row) == abs(start_col - end_col):
            step_row = 1 if end_row > start_row else -1
            step_col = 1 if end_col > start_col else -1
            current_row, current_col = start_row + step_row, start_col + step_col
            valid = True
            while current_row != end_row:
                if board[current_row][current_col] != '--':
                    valid = False
                    break
                current_row += step_row
                current_col += step_col

    elif piece_type == 'queen':
        if start_row == end_row or start_col == end_col or abs(start_row - end_row) == abs(start_col - end_col):
            step_row = 0 if start_row == end_row else (1 if end_row > start_row else -1)
            step_col = 0 if start_col == end_col else (1 if end_col > start_col else -1)
            current_row, current_col = start_row + step_row, start_col + step_col
            valid = True
            while current_row != end_row or current_col != end_col:
                if board[current_row][current_col] != '--':
                    valid = False
                    break
                current_row += step_row
                current_col += step_col

    elif piece_type == 'king':
        if max(abs(start_row - end_row), abs(start_col - end_col)) == 1:
            valid = True

    # After movement logic, if check_check is True, simulate the move and check for check
    if valid and check_check:
        # Simulate the move
        new_board = [row.copy() for row in board]
        new_board[end_row][end_col] = piece
        new_board[start_row][start_col] = '--'
        if is_in_check(piece_color, new_board):
            return False  # Move leaves king in check

    return valid


def draw_turn_indicator():
    text = f"{'White' if current_player == 'w' else 'Black'}'s Turn"
    img = font.render(text, True, BLACK)
    screen.blit(img, (20, 20))


def handle_click(board, pos):
    global selected_piece, selected_position, current_player
    board_x, board_y = [(screen_dim - 8 * SQUARE_SIZE) // 2 for screen_dim in (screen.get_width(), screen.get_height())]
    x, y = pos
    col = (x - board_x) // SQUARE_SIZE
    row = (y - board_y) // SQUARE_SIZE
    if 0 <= row < 8 and 0 <= col < 8:
        if selected_piece:
            # Move the piece if the move is valid
            if is_valid_move(selected_piece, selected_position, (row, col), board):
                board[row][col] = selected_piece
                board[selected_position[0]][selected_position[1]] = '--'
                # Switch turn
                current_player = 'b' if current_player == 'w' else 'w'
            selected_piece = None
            selected_position = None
        else:
            # Select a piece of the current player
            if board[row][col] != '--' and board[row][col][0] == current_player:
                selected_piece = board[row][col]
                selected_position = (row, col)


# Main game loop
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.VIDEORESIZE:
            new_width = max(event.w, MIN_WIDTH)
            new_height = max(event.h, MIN_HEIGHT)
            screen = pg.display.set_mode((new_width, new_height), pg.RESIZABLE)
            background = pg.transform.smoothscale(pg.image.load('images/woodbackground.jpeg'), (screen.get_width(), screen.get_height()))
            resize_pieces()
        elif event.type == pg.MOUSEBUTTONDOWN:
            handle_click(board, event.pos)

    # Draw everything
    draw_board()
    draw_pieces(board)

    # Update the display
    draw_turn_indicator()
    pg.display.flip()

pg.quit()
sys.exit()