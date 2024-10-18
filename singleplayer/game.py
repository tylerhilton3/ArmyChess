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
LIGHT_BROWN = (237, 214, 176)
DARK_BROWN = (184, 135, 98)
GRAY = (80, 80, 80)
LIGHT_YELLOW = (246, 234, 113)
DARK_YELLOW = (219, 195, 74)
LIGHT_GRAY = (204, 184, 151)
DARK_GRAY = (158, 116, 84)
DARK_GRAY_HIGHLIGHT = (188, 168, 64)
LIGHT_GRAY_HIGHLIGHT = (211, 201, 97)

WHITE_TIME = 3  # 5 minutes in seconds (adjust as needed)
BLACK_TIME = 300  # 5 minutes in seconds (adjust as needed)
last_tick = pg.time.get_ticks()  # To track elapsed time

def update_timers():
    global WHITE_TIME, BLACK_TIME, last_tick

    current_tick = pg.time.get_ticks()
    time_delta = (current_tick - last_tick) / 1000  # Convert milliseconds to seconds
    last_tick = current_tick

    # Deduct time from the current player's clock
    if current_player == 'w':
        WHITE_TIME -= time_delta
        if WHITE_TIME <= 0:
            draw_endgame_message("Black wins on time!")
            pg.time.delay(3000)
            pg.quit()
            sys.exit()
    else:
        BLACK_TIME -= time_delta
        if BLACK_TIME <= 0:
            draw_endgame_message("White wins on time!")
            pg.time.delay(3000)
            pg.quit()
            sys.exit()

def draw_timers():
    # Convert remaining time to minutes:seconds format
    white_minutes = int(WHITE_TIME // 60)
    white_seconds = int(WHITE_TIME % 60)
    black_minutes = int(BLACK_TIME // 60)
    black_seconds = int(BLACK_TIME % 60)

    white_time_text = f"White: {white_minutes:02}:{white_seconds:02}"
    black_time_text = f"Black: {black_minutes:02}:{black_seconds:02}"

    # Render the timer text surfaces
    white_timer_surface = font.render(white_time_text, True, WHITE)
    black_timer_surface = font.render(black_time_text, True, BLACK)

    # Get the rect (bounding box) of the text surface to center the background
    white_timer_rect = white_timer_surface.get_rect(topleft=(20, 60))  # White's timer position
    black_timer_rect = black_timer_surface.get_rect(topleft=(20, 100))  # Black's timer position

    # Create background surface slightly larger than the text (for padding)
    padding = 10
    white_bg_rect = pg.Rect(
        white_timer_rect.left - padding // 2,
        white_timer_rect.top - padding // 2,
        white_timer_rect.width + padding,
        white_timer_rect.height + padding
    )
    black_bg_rect = pg.Rect(
        black_timer_rect.left - padding // 2,
        black_timer_rect.top - padding // 2,
        black_timer_rect.width + padding,
        black_timer_rect.height + padding
    )

    # Create semi-transparent background surfaces for the timers
    white_bg_surface = pg.Surface(white_bg_rect.size)
    white_bg_surface.fill(DARK_BROWN)  # Black background

    black_bg_surface = pg.Surface(black_bg_rect.size)
    black_bg_surface.fill(DARK_BROWN)

    # Blit the background surfaces behind the timers
    screen.blit(white_bg_surface, white_bg_rect.topleft)
    screen.blit(black_bg_surface, black_bg_rect.topleft)

    # Blit the text on top of the backgrounds
    screen.blit(white_timer_surface, white_timer_rect.topleft)
    screen.blit(black_timer_surface, black_timer_rect.topleft)


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
    return pg.image.load(f'singleplayer/images/{name}.png').convert_alpha()

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
    filepath = f'singleplayer/sounds{goofy*"goofy"}/{name}.mp3'
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"{filepath} does not exist.")
    sound = pg.mixer.Sound(filepath)
    sound.set_volume(master_volume)
    return sound

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

background = pg.transform.smoothscale(pg.image.load('singleplayer/images/woodbackground.jpeg'), (screen.get_width(), screen.get_height()))
font = pg.font.SysFont(None, 36)

current_player = 'w'
en_passant_target = None
castling_rights = {
    'w': {'K': True, 'Q': True},
    'b': {'K': True, 'Q': True}
}
valid_moves = []
last_move = {'w': None, 'b': None}
half_move_counter = 0
board_states = []

def store_board_state(board):
    # Convert the board to a string representation to track positions
    board_string = ''.join([''.join(row) for row in board]) + current_player
    board_states.append(board_string)

BOARD_MARGIN = int(screen.get_height() * 0.1)

def resize_pieces():
    global SQUARE_SIZE, pieces
    SQUARE_SIZE = (min(screen.get_width(), screen.get_height()) - int(screen.get_height() * 0.1) * 2) // 8
    for key in pieces:
        pieces[key] = pg.transform.smoothscale(original_pieces[key], (SQUARE_SIZE, SQUARE_SIZE))

resize_pieces()

def draw_board():
    screen.blit(background, (0, 0))
    board_width = 8 * SQUARE_SIZE
    board_height = 8 * SQUARE_SIZE
    board_x = (screen.get_width() - board_width) // 2
    board_y = (screen.get_height() - board_height) // 2
    colors = [LIGHT_BROWN, DARK_BROWN]
    border_width = SQUARE_SIZE // 8
    border_rect = pg.Rect(board_x - border_width, board_y - border_width, board_width + 2 * border_width, board_height + 2 * border_width)
    pg.draw.rect(screen, BLACK, border_rect)
    opponent_color = 'b' if current_player == 'w' else 'w'
    for row in range(8):
        for col in range(8):
            base_color = colors[(row + col) % 2]
            color = base_color
            if selected_position == (row, col):
                color = LIGHT_YELLOW if base_color == LIGHT_BROWN else DARK_YELLOW
            elif last_move[opponent_color]:
                from_pos, to_pos = last_move[opponent_color]
                if from_pos == (row, col) or to_pos == (row, col):
                    color = LIGHT_YELLOW if base_color == LIGHT_BROWN else DARK_YELLOW
            rect = pg.Rect(board_x + col * SQUARE_SIZE, board_y + row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pg.draw.rect(screen, color, rect)

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
    king_position = None
    for row in range(8):
        for col in range(8):
            if board[row][col] == f'{player_color}_king':
                king_position = (row, col)
                break
        if king_position:
            break

    if king_position is None:
        return False  # No king on the board (edge case)

    print(f"{player_color} king's position: {king_position}")
    opponent_color = 'b' if player_color == 'w' else 'w'

    # Check for threats from all opponent pieces
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece.startswith(opponent_color):
                # Check if the piece can move to the king's position
                if is_valid_move(piece, (row, col), king_position, board, check_check=False):
                    print(f"{opponent_color} piece at {(row, col)} can check {player_color}'s king.")
                    return True
    return False

def is_checkmate(player_color, board):
    if not is_in_check(player_color, board):
        print(f"{player_color} is not in check.")
        return False

    print(f"{player_color} is in check. Checking for valid moves...")

    # Try to find a valid move that would prevent checkmate
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece.startswith(player_color):
                valid_moves = get_valid_moves(piece, (row, col), board)
                for move in valid_moves:
                    end_pos, _ = move
                    new_board = [r.copy() for r in board]
                    new_board[end_pos[0]][end_pos[1]] = piece
                    new_board[row][col] = '--'

                    # Check if the player is still in check after this move
                    if not is_in_check(player_color, new_board):
                        print(f"Found a valid move for {player_color}'s piece at {(row, col)} to {end_pos}. Not checkmate.")
                        return False  # There's a valid move to escape check

    print(f"{player_color} is checkmated!")
    return True  # No valid moves and in check, so it's checkmate

def is_stalemate(player_color, board):
    if is_in_check(player_color, board):
        print(f"{player_color} is in check, so it can't be stalemate.")
        return False

    # Debugging: Print statement to verify the lack of valid moves
    print(f"{player_color} is not in check. Checking for valid moves...")

    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece.startswith(player_color):
                valid_moves = get_valid_moves(piece, (row, col), board)
                # Debugging: Print valid moves for each piece
                print(f"{player_color}'s piece {piece} at {(row, col)} has valid moves: {valid_moves}")
                if valid_moves:
                    print(f"{player_color} has valid moves, so it's not stalemate.")
                    return False

    print(f"{player_color} has no valid moves left and is not in check. Stalemate!")
    return True

def threefoldrep():
    # Count how many times the current board state has occurred
    current_state = ''.join([''.join(row) for row in board]) + current_player
    occurrences = board_states.count(current_state)
    
    if occurrences >= 3:
        return True
    return False


def is_50_move():
    # If half_move_counter reaches 100, it means 50 moves have been made without a pawn move or capture
    if half_move_counter >= 10:
        print("50-move rule triggered! It's a draw.")
        return True
    return False

def can_castle(color, start, end, board):
    start_row, start_col = start
    end_row, end_col = end
    if not castling_rights[color]['K'] and end_col > start_col:
        return False
    if not castling_rights[color]['Q'] and end_col < start_col:
        return False
    if end_col > start_col:
        rook_col = 7
        step = 1
    else:
        rook_col = 0
        step = -1
    rook_piece = board[start_row][rook_col]
    if rook_piece != f'{color}_rook':
        return False
    for col in range(start_col + step, rook_col, step):
        if board[start_row][col] != '--':
            return False
        temp_board = [row.copy() for row in board]
        temp_board[start_row][col] = f'{color}_king'
        temp_board[start_row][start_col] = '--'
        if is_in_check(color, temp_board):
            return False
    if is_in_check(color, board):
        return False
    return True

def promote_pawn(color):
    promotion_surface = pg.Surface((4 * SQUARE_SIZE, SQUARE_SIZE))
    promotion_surface.set_alpha(230)
    promotion_surface.fill(GRAY)
    pieces_list = ['queen', 'rook', 'bishop', 'knight']
    piece_images = [pieces[f'{color}_{piece_name}'] for piece_name in pieces_list]
    screen_rect = screen.get_rect()
    x = screen_rect.centerx - 2 * SQUARE_SIZE
    y = screen_rect.centery - SQUARE_SIZE // 2
    promotion_rect = pg.Rect(x, y, 4 * SQUARE_SIZE, SQUARE_SIZE)
    screen.blit(promotion_surface, (x, y))
    for i, img in enumerate(piece_images):
        img_rect = img.get_rect()
        img_rect.topleft = (x + i * SQUARE_SIZE, y)
        screen.blit(img, img_rect)
    pg.display.flip()
    while True:
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if promotion_rect.collidepoint(mouse_x, mouse_y):
                    index = (mouse_x - x) // SQUARE_SIZE
                    if 0 <= index < 4:
                        return f'{color}_{pieces_list[index]}'
            elif event.type == pg.QUIT:
                pg.quit()
                sys.exit()

selected_piece = None
selected_position = None

def is_valid_move(piece, start, end, board, check_check=True):
    global en_passant_target
    if start == end:
        return False
    start_row, start_col = start
    end_row, end_col = end
    piece_type = piece[2:]
    piece_color = piece[0]
    target_piece = board[end_row][end_col]
    if target_piece != '--' and target_piece[0] == piece_color:
        return False
    valid = False
    if piece_type == 'pawn':
        direction = -1 if piece_color == 'w' else 1
        if start_col == end_col and board[end_row][end_col] == '--':
            if end_row == start_row + direction:
                valid = True
            elif (start_row == 1 and piece_color == 'b') or (start_row == 6 and piece_color == 'w'):
                if end_row == start_row + 2 * direction and board[start_row + direction][start_col] == '--':
                    valid = True
        elif abs(start_col - end_col) == 1 and end_row == start_row + direction:
            if target_piece != '--' and target_piece[0] != piece_color:
                valid = True
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
        elif start_row == end_row and abs(start_col - end_col) == 2:
            if can_castle(piece_color, start, end, board):
                valid = True
    if valid and check_check:
        new_board = [row.copy() for row in board]
        new_board[end_row][end_col] = piece
        new_board[start_row][start_col] = '--'
        if piece_type == 'pawn' and abs(start_col - end_col) == 1 and end_row == start_row + direction:
            if board[end_row][end_col] == '--' and en_passant_target == (end_row, end_col):
                new_board[start_row][end_col] = '--'
        if piece_type == 'king' and abs(start_col - end_col) == 2:
            if end_col > start_col:
                rook_col = 7
                new_rook_col = start_col + 1
            else:
                rook_col = 0
                new_rook_col = start_col - 1
            new_board[start_row][new_rook_col] = new_board[start_row][rook_col]
            new_board[start_row][rook_col] = '--'
        if is_in_check(piece_color, new_board):
            return False
    return valid

def get_valid_moves(piece, position, board):
    valid_moves = []
    for row in range(8):
        for col in range(8):
            if is_valid_move(piece, position, (row, col), board):
                target_piece = board[row][col]
                move_type = 'move' if target_piece == '--' else 'capture'
                valid_moves.append(((row, col), move_type))

    # Debugging: Print valid moves for this piece
    print(f"{piece} at {position} has valid moves: {valid_moves}")
    return valid_moves

def draw_turn_indicator():
    text = f"{'White' if current_player == 'w' else 'Black'}'s Turn"
    img = font.render(text, True, BLACK)
    screen.blit(img, (20, 20))

def handle_click(board, pos):
    global selected_piece, selected_position, current_player, en_passant_target, castling_rights, valid_moves, half_move_counter
    board_x, board_y = [(screen.get_width() - 8 * SQUARE_SIZE) // 2, (screen.get_height() - 8 * SQUARE_SIZE) // 2]
    x, y = pos
    col = (x - board_x) // SQUARE_SIZE
    row = (y - board_y) // SQUARE_SIZE

    if 0 <= row < 8 and 0 <= col < 8:
        piece_at_square = board[row][col]
        # Check if a piece is selected
        if piece_at_square != '--' and piece_at_square[0] == current_player:
            selected_piece = piece_at_square
            selected_position = (row, col)
            valid_moves = get_valid_moves(selected_piece, selected_position, board)
        elif selected_piece:
            valid_move = is_valid_move(selected_piece, selected_position, (row, col), board)
            if valid_move:
                target_piece = board[row][col]  # Assign target_piece here when a valid move is attempted
                en_passant_capture = False
                if selected_piece[2:] == 'pawn' and (row, col) == en_passant_target:
                    en_passant_capture = True
                castling_move = False
                if selected_piece[2:] == 'king' and abs(selected_position[1] - col) == 2:
                    castling_move = True
                board[row][col] = selected_piece
                board[selected_position[0]][selected_position[1]] = '--'
                last_move[current_player] = (selected_position, (row, col))
                
                # Reset the half-move counter for a pawn move or capture
                if selected_piece[2:] == 'pawn' or target_piece != '--':
                    half_move_counter = 0
                else:
                    half_move_counter += 1

                if selected_piece[2:] == 'pawn' and (row == 0 or row == 7):
                    promoted_piece = promote_pawn(selected_piece[0])
                    board[row][col] = promoted_piece
                    if sounds['promote']:
                        sounds['promote'].play()
                if en_passant_capture:
                    direction = -1 if selected_piece[0] == 'w' else 1
                    board[row - direction][col] = '--'
                    if sounds['capture']:
                        sounds['capture'].play()
                elif castling_move:
                    if col > selected_position[1]:
                        rook_col = 7
                        new_rook_col = selected_position[1] + 1
                    else:
                        rook_col = 0
                        new_rook_col = selected_position[1] - 1
                    board[row][new_rook_col] = board[row][rook_col]
                    board[row][rook_col] = '--'
                    castling_rights[current_player]['K'] = False
                    castling_rights[current_player]['Q'] = False
                    if sounds['castle']:
                        sounds['castle'].play()
                else:
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

                # Check for checkmate after every move
                opponent_color = 'b' if current_player == 'w' else 'w'
                store_board_state(board)
                
                if is_checkmate(opponent_color, board):
                    print(f"Checkmate! {opponent_color.capitalize()} is checkmated. {current_player.capitalize()} wins!")
                    
                    draw_endgame_message(f"Checkmate! {"White" if opponent_color.capitalize() == "W" else "Black"} is checkmated. {"White" if opponent_color.capitalize() == "B" else "Black"} wins!")
                    pg.time.delay(3000)
                    pg.quit()
                    sys.exit()

                # Check for stalemate
                if is_stalemate(opponent_color, board):
                    print("Draw by stalemate!")

                    draw_endgame_message("Draw by stalemate!")
                    pg.time.delay(3000)
                    pg.quit()
                    sys.exit()

                if is_50_move():
                    draw_endgame_message("Draw by 50-move rule!")
                    pg.time.delay(3000)
                    pg.quit()
                    sys.exit()
                
                if threefoldrep():
                    print("Draw by 3-fold repetition!")

                    draw_endgame_message("Draw by 3-fold repetition!")
                    pg.time.delay(3000)
                    pg.quit()
                    sys.exit()

                # Switch the turn
                current_player = 'b' if current_player == 'w' else 'w'
                piece_type = selected_piece[2:]
                if piece_type == 'pawn' and abs(selected_position[0] - row) == 2:
                    en_passant_target = ((selected_position[0] + row) // 2, selected_position[1])
                else:
                    en_passant_target = None

            selected_piece = None
            selected_position = None
            valid_moves = []
        else:
            if board[row][col] != '--' and board[row][col][0] == current_player:
                selected_piece = board[row][col]
                selected_position = (row, col)
                valid_moves = get_valid_moves(selected_piece, selected_position, board)




def draw_valid_moves():
    if not selected_piece:
        return
    board_width = 8 * SQUARE_SIZE
    board_height = 8 * SQUARE_SIZE
    board_x = (screen.get_width() - board_width) // 2
    board_y = (screen.get_height() - board_height) // 2
    for move in valid_moves:
        (row, col), move_type = move
        base_color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
        highlight_color = LIGHT_GRAY
        if base_color == LIGHT_BROWN:
            highlight_color = LIGHT_GRAY_HIGHLIGHT if (row, col) == selected_position else LIGHT_GRAY
        elif base_color == DARK_BROWN:
            highlight_color = DARK_GRAY_HIGHLIGHT if (row, col) == selected_position else DARK_GRAY
        elif base_color == LIGHT_YELLOW:
            highlight_color = LIGHT_GRAY_HIGHLIGHT
        elif base_color == DARK_YELLOW:
            highlight_color = DARK_GRAY_HIGHLIGHT
        center_x = board_x + col * SQUARE_SIZE + SQUARE_SIZE // 2
        center_y = board_y + row * SQUARE_SIZE + SQUARE_SIZE // 2
        if move_type == 'move':
            radius = SQUARE_SIZE // 6
            circle_surface = pg.Surface((SQUARE_SIZE, SQUARE_SIZE), pg.SRCALPHA)
            pg.draw.circle(circle_surface, highlight_color, (SQUARE_SIZE // 2, SQUARE_SIZE // 2), radius)
            screen.blit(circle_surface, (board_x + col * SQUARE_SIZE, board_y + row * SQUARE_SIZE))
        elif move_type == 'capture':
            radius = SQUARE_SIZE // 2 - SQUARE_SIZE // 16
            pg.draw.circle(screen, highlight_color, (center_x, center_y), radius, width=SQUARE_SIZE // 16)

def draw_endgame_message(message):
    # Create a semi-transparent overlay for the message
    overlay = pg.Surface((screen.get_width(), screen.get_height()))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))  # Black overlay

    # Render the message text
    font_large = pg.font.SysFont(None, 72)
    text_surface = font_large.render(message, True, WHITE)
    text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))

    # Draw the overlay and message
    screen.blit(overlay, (0, 0))
    screen.blit(text_surface, text_rect)
    pg.display.flip()

    # Wait for the user to close the game
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_RETURN):
                pg.quit()
                sys.exit()

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.VIDEORESIZE:
            new_width = max(event.w, MIN_WIDTH)
            new_height = max(event.h, MIN_HEIGHT)
            screen = pg.display.set_mode((new_width, new_height), pg.RESIZABLE)
            background = pg.transform.smoothscale(pg.image.load('singleplayer/images/woodbackground.jpeg'), (screen.get_width(), screen.get_height()))
            resize_pieces()
        elif event.type == pg.MOUSEBUTTONDOWN:
            handle_click(board, event.pos)
    if is_50_move():
        print("Draw by the 50-move rule!")
        pg.quit()
        sys.exit()
    update_timers()
    draw_board()
    draw_pieces(board)
    draw_valid_moves()
    draw_turn_indicator()
    draw_timers()
    pg.display.flip()

pg.quit()
sys.exit()
