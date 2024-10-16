import pygame as pg
import sys
import os

pg.init()
pg.mixer.init()
pg.display.set_caption('Army Chess')

MIN_WIDTH, MIN_HEIGHT = 640, 480
screen = pg.display.set_mode((1280, 720), pg.RESIZABLE)
SQUARE_SIZE = int(screen.get_height() * 0.8) // 8

WHITE, BLACK = (255, 255, 255), (0, 0, 0)
LIGHT_BROWN = (220, 185, 140)
DARK_BROWN = (120, 60, 40)
GRAY = (80, 80, 80)
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
master_volume = 1.0
def load_sound(name, goofy):
    try:
        filepath = f'sounds{goofy*"goofy"}/{name}.mp3'
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"{filepath} does not exist.")
        sound = pg.mixer.Sound(filepath)
        sound.set_volume(master_volume)  # Set the initial volume
        return sound
    except (pg.error, FileNotFoundError) as e:
        print(f"Unable to load sound {name}.mp3: {e}")
        return None
goofy = False
sounds = {
    'move': load_sound('move', goofy),
    'capture': load_sound('capture', goofy),
    'castle': load_sound('castle', goofy),
    'move_check': load_sound('move-check', goofy),
    'promote': load_sound('promote', goofy),
}
def set_master_volume(volume):
    global master_volume
    master_volume = volume
    for sound in sounds.values():
        if sound:
            sound.set_volume(master_volume)
set_master_volume(0.1)


background = pg.transform.smoothscale(pg.image.load('images/woodbackground.jpeg'), (screen.get_width(), screen.get_height()))
font = pg.font.SysFont(None, 36)

current_player = 'w'
en_passant_target = None
castling_rights = {
    'w': {'K': True, 'Q': True},  # King-side and Queen-side castling
    'b': {'K': True, 'Q': True}
}
valid_moves = []


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

def can_castle(color, start, end, board):
    # Castling conditions
    start_row, start_col = start
    end_row, end_col = end

    # King must not have moved
    if not castling_rights[color]['K'] and end_col > start_col:
        return False
    if not castling_rights[color]['Q'] and end_col < start_col:
        return False

    # Path between king and rook must be clear
    if end_col > start_col:
        # King-side castling
        rook_col = 7
        step = 1
    else:
        # Queen-side castling
        rook_col = 0
        step = -1

    # Check that rook is in the correct position and hasn't moved
    rook_piece = board[start_row][rook_col]
    if rook_piece != f'{color}_rook':
        return False
    if (end_col > start_col and not castling_rights[color]['K']) or (end_col < start_col and not castling_rights[color]['Q']):
        return False

    # Check the path is clear and not under attack
    for col in range(start_col + step, rook_col, step):
        if board[start_row][col] != '--':
            return False
        # Simulate moving through squares to check for attack
        if col != start_col:
            temp_board = [row.copy() for row in board]
            temp_board[start_row][col] = f'{color}_king'
            temp_board[start_row][start_col] = '--'
            if is_in_check(color, temp_board):
                return False
    # Check that king is not currently in check
    if is_in_check(color, board):
        return False

    return True

def promote_pawn(color):
    # Create a surface for the promotion choices
    promotion_surface = pg.Surface((4 * SQUARE_SIZE, SQUARE_SIZE))
    promotion_surface.set_alpha(230)
    promotion_surface.fill(GRAY)
    
    # Load the images of the pieces
    pieces_list = ['queen', 'rook', 'bishop', 'knight']
    piece_images = []
    for piece_name in pieces_list:
        piece_key = f'{color}_{piece_name}'
        piece_images.append(pieces[piece_key])
    
    # Position the promotion surface in the center
    screen_rect = screen.get_rect()
    x = screen_rect.centerx - 2 * SQUARE_SIZE
    y = screen_rect.centery - SQUARE_SIZE // 2
    promotion_rect = pg.Rect(x, y, 4 * SQUARE_SIZE, SQUARE_SIZE)
    
    # Blit the promotion surface onto the screen
    screen.blit(promotion_surface, (x, y))
    
    # Blit the piece images onto the promotion surface
    for i, img in enumerate(piece_images):
        img_rect = img.get_rect()
        img_rect.topleft = (x + i * SQUARE_SIZE, y)
        screen.blit(img, img_rect)
    
    pg.display.flip()
    
    # Wait for the player to click on one of the pieces
    while True:
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if promotion_rect.collidepoint(mouse_x, mouse_y):
                    # Determine which piece was clicked
                    index = (mouse_x - x) // SQUARE_SIZE
                    if 0 <= index < 4:
                        chosen_piece = f'{color}_{pieces_list[index]}'
                        return chosen_piece
            elif event.type == pg.QUIT:
                pg.quit()
                sys.exit()

selected_piece = None
selected_position = None
def is_valid_move(piece, start, end, board, check_check=True):
    global en_passant_target  # Access the en passant target
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
        elif abs(start_col - end_col) == 1 and end_row == start_row + direction:
            # Normal capture
            if target_piece != '--' and target_piece[0] != piece_color:
                valid = True
            # En passant capture
            elif board[end_row][end_col] == '--' and en_passant_target == (end_row, end_col):
                if board[start_row][end_col][0] != piece_color and board[start_row][end_col][2:] == 'pawn':
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
        # Castling logic moved here
        elif start_row == end_row and abs(start_col - end_col) == 2:
            # King-side or Queen-side castling
            if can_castle(piece_color, start, end, board):
                valid = True

    # After movement logic, if check_check is True, simulate the move and check for check
    if valid and check_check:
        # Simulate the move
        new_board = [row.copy() for row in board]
        new_board[end_row][end_col] = piece
        new_board[start_row][start_col] = '--'

        # Handle en passant capture in simulation
        if piece_type == 'pawn' and abs(start_col - end_col) == 1 and end_row == start_row + direction:
            # En passant capture
            if board[end_row][end_col] == '--' and en_passant_target == (end_row, end_col):
                # Remove the captured pawn in simulation
                new_board[start_row][end_col] = '--'

        # Handle castling in simulation
        if piece_type == 'king' and abs(start_col - end_col) == 2:
            # Move the rook in the simulation
            if end_col > start_col:
                rook_col = 7
                new_rook_col = start_col + 1
            else:
                rook_col = 0
                new_rook_col = start_col - 1
            new_board[start_row][new_rook_col] = new_board[start_row][rook_col]
            new_board[start_row][rook_col] = '--'

        if is_in_check(piece_color, new_board):
            return False  # Move leaves king in check

    return valid

def get_valid_moves(piece, position, board):
    valid_moves = []
    for row in range(8):
        for col in range(8):
            if is_valid_move(piece, position, (row, col), board):
                target_piece = board[row][col]
                if target_piece == '--':
                    move_type = 'move'  # Regular move to an empty square
                else:
                    move_type = 'capture'  # Capture move
                valid_moves.append(((row, col), move_type))
    return valid_moves


def draw_turn_indicator():
    text = f"{'White' if current_player == 'w' else 'Black'}'s Turn"
    img = font.render(text, True, BLACK)
    screen.blit(img, (20, 20))

def handle_click(board, pos):
    global selected_piece, selected_position, current_player, en_passant_target, castling_rights
    board_x, board_y = [(screen.get_width() - 8 * SQUARE_SIZE) // 2, (screen.get_height() - 8 * SQUARE_SIZE) // 2]
    x, y = pos
    col = (x - board_x) // SQUARE_SIZE
    row = (y - board_y) // SQUARE_SIZE
    if 0 <= row < 8 and 0 <= col < 8:
        if selected_piece:
            # Check if the move is valid
            valid_move = is_valid_move(selected_piece, selected_position, (row, col), board)
            if valid_move:
                target_piece = board[row][col]
                # En passant capture check before moving the piece
                en_passant_capture = False
                if selected_piece[2:] == 'pawn' and (row, col) == en_passant_target:
                    en_passant_capture = True

                # Castling check
                castling_move = False
                if selected_piece[2:] == 'king' and abs(selected_position[1] - col) == 2:
                    castling_move = True

                # Move the piece
                board[row][col] = selected_piece
                board[selected_position[0]][selected_position[1]] = '--'

                if selected_piece[2:] == 'pawn' and (row == 0 or row == 7):
                    # Pawn has reached the back rank
                    # Handle promotion
                    promoted_piece = promote_pawn(selected_piece[0])  # Function to handle promotion
                    board[row][col] = promoted_piece
                    # Play promotion sound
                    if sounds['promote']:
                        sounds['promote'].play()
                # En passant capture
                if en_passant_capture:
                    # Remove the captured pawn
                    direction = -1 if selected_piece[0] == 'w' else 1
                    board[row - direction][col] = '--'
                    # Play capture sound
                    if sounds['capture']:
                        sounds['capture'].play()
                elif castling_move:
                    # Move the rook
                    if col > selected_position[1]:
                        # King-side castling
                        rook_col = 7
                        new_rook_col = selected_position[1] + 1
                    else:
                        # Queen-side castling
                        rook_col = 0
                        new_rook_col = selected_position[1] - 1
                    board[row][new_rook_col] = board[row][rook_col]
                    board[row][rook_col] = '--'
                    # Update castling rights
                    castling_rights[current_player]['K'] = False
                    castling_rights[current_player]['Q'] = False
                    # Play castle sound
                    if sounds['castle']:
                        sounds['castle'].play()
                else:
                    # Check if move puts opponent in check
                    opponent_color = 'b' if current_player == 'w' else 'w'
                    if is_in_check(opponent_color, board):
                        # Play move-check sound
                        if sounds['move_check']:
                            sounds['move_check'].play()
                    else:
                        # Play move or capture sound
                        if target_piece != '--' and target_piece[0] != current_player:
                            if sounds['capture']:
                                sounds['capture'].play()
                        else:
                            if sounds['move']:
                                sounds['move'].play()

                # Update castling rights if king or rook has moved
                if selected_piece[2:] == 'king':
                    castling_rights[current_player]['K'] = False
                    castling_rights[current_player]['Q'] = False
                elif selected_piece[2:] == 'rook':
                    if selected_position[1] == 0:
                        castling_rights[current_player]['Q'] = False
                    elif selected_position[1] == 7:
                        castling_rights[current_player]['K'] = False

                # Switch turn
                current_player = 'b' if current_player == 'w' else 'w'

                # Update en passant target
                piece_type = selected_piece[2:]
                if piece_type == 'pawn' and abs(selected_position[0] - row) == 2:
                    # Pawn moved two squares forward
                    en_passant_target = ((selected_position[0] + row) // 2, selected_position[1])
                else:
                    en_passant_target = None

            selected_piece = None
            selected_position = None
            valid_moves = []
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
