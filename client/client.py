import pygame as pg
import sys
import os
import firebase_admin
from firebase_admin import credentials, db
import time as t
import json


### DATABASE SETUP

cred = credentials.Certificate("client/firebaseprivatekey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://army-chess-default-rtdb.firebaseio.com/'
})


def gameinit(game_id):
    with open('client/game.json', 'r') as file:
        data = json.load(file)
    ref = db.reference(f'/games/game{game_id}')
    ref.set(data)

def remove_old_games():
    games_data = db.reference("games").get()
    if games_data == None:
        return
    for gameid, gamedata in games_data.items():
        connections = gamedata['connections']
        if connections.get('black') == False and connections.get('white') == False:
            gamedelete = db.reference('games').child(gameid)
            gamedelete.delete()
            print(f'game{gameid} has been deleted.')

remove_old_games()

youareblack = False
game_id = 0
gameexist = True
while gameexist:
    game_id += 1
    game_ref = db.reference(f"games/game{game_id}")
    gameexist = bool(game_ref.get())
    if gameexist and game_ref.child("connections").child("white").get() and not game_ref.child("connections").child("black").get():
        gameexist = False
        youareblack = True

if not youareblack:
    print("initializing game because you're white")
    gameinit(game_id)


game = db.reference(f'/games/game{game_id}')
whiteconn = db.reference(f"games/game{game_id}/connections/white")
blackconn = db.reference(f"games/game{game_id}/connections/black")


blackconnected = False
correct = False
if not whiteconn.get():
    player = 1
    opp = 2
    print(f"You are White.")
    whiteconn.set(True)
    print("Waiting for Black...")
    while not blackconnected:
        blackconnected = blackconn.get()
else:
    player = 2
    opp = 1
    print("You are Black.")
    while not correct:
        try:
            GAME_ID = int(input("Which game would you like to connect to?: "))
            if f"game{GAME_ID}" not in db.reference("games").get():
                print("Game ID does not exist. Please try another.")
                correct = False
            else:
                correct = True
        except:
            print("Please enter an integer game ID.")            
    blackconn.set(True)
    blackconnected = True


print("Finished connecting!")
print(f"you are player {player}")



### DISPLAY

pg.init()
pg.mixer.init()
pg.display.set_caption('Army Chess')

MIN_WIDTH, MIN_HEIGHT = 640, 480
screen = pg.display.set_mode((1280, 720), pg.RESIZABLE)
SQUARE_SIZE = int(screen.get_height() * 0.8) // 8
BOARD_MARGIN = int(screen.get_height() * 0.1)

background = pg.transform.smoothscale(pg.image.load('singleplayer/images/woodbackground.jpeg'), (screen.get_width(), screen.get_height()))
font = pg.font.SysFont(None, 36)

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



### IMAGES

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

iconpath = "client/assets/images/icon64.ico"
icon = pg.image.load(iconpath)
pg.display.set_icon(icon)

### SOUND

def load_sound(name, goofy):
    filepath = f'singleplayer/sounds{goofy*"goofy"}/{name}.mp3'
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"{filepath} does not exist.")
    sound = pg.mixer.Sound(filepath)
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
    for sound in sounds.values():
        if sound:
            sound.set_volume(volume)
set_master_volume(0.2)



### BOARD AND GAME DATA

def invert(inputboard):
    return [row[::-1] for row in inputboard[::-1]]
    
selected_piece = None
selected_position = None

gref = db.reference(f"/games/game{game_id}")

def gameupdate(event):
    global current_player, castling_rights, board, en_passant_target, last_move, half_move_counter, board_states
    current_player = gref.child("current_player").get()
    castling_rights = gref.child("castling_rights").get()
    board = gref.child("board").get() if player == 1 else invert(gref.child("board").get())
    en_passant_target = gref.child("en_passant_target").get()
    last_move = gref.child("last_move").get()
    half_move_counter = gref.child("half_move_counter").get()
    board_states = gref.child("board_states").get()
    print("OMG SOMETHING HAPPENEDDDDDD")

gameupdate("wheeeeeeee")
gameupdate_listener = gref.listen(gameupdate)

def store_board_state(board):
    board_string = ''.join([''.join(row) for row in board]) + current_player
    board_states.append(board_string)

def resize_pieces():
    global SQUARE_SIZE, pieces
    SQUARE_SIZE = (min(screen.get_width(), screen.get_height()) - int(screen.get_height() * 0.1) * 2) // 8
    for key in pieces:
        pieces[key] = pg.transform.smoothscale(original_pieces[key], (SQUARE_SIZE, SQUARE_SIZE))

resize_pieces()



### DRAWING FUNCTIONS

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

def draw_turn_indicator():
    text = f"{'White' if current_player == 'w' else 'Black'}'s Turn"
    img = font.render(text, True, BLACK)
    screen.blit(img, (20, 20))

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
    overlay = pg.Surface((screen.get_width(), screen.get_height()))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))

    font_large = pg.font.SysFont(None, 72)
    font_small = pg.font.SysFont(None, 48)

    text_surface1 = font_large.render(message, True, WHITE)
    text_rect1 = text_surface1.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50))

    light_gray = (200, 200, 200)
    text_surface2 = font_small.render("Click anywhere to restart", True, light_gray)
    text_rect2 = text_surface2.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50))

    screen.blit(overlay, (0, 0))
    screen.blit(text_surface1, text_rect1)
    screen.blit(text_surface2, text_rect2)

    pg.display.flip()



### GAME LOGIC

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
        return False
    opponent_color = 'b' if player_color == 'w' else 'w'

    
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece.startswith(opponent_color):
                
                if is_valid_move(piece, (row, col), king_position, check_check=False):
                    return True
    return False

def is_checkmate(player_color, board):
    if not is_in_check(player_color, board):
        return False

    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece.startswith(player_color):
                valid_moves = get_valid_moves(piece, (row, col))
                for move in valid_moves:
                    end_pos, _ = move
                    new_board = [r.copy() for r in board]
                    new_board[end_pos[0]][end_pos[1]] = piece
                    new_board[row][col] = '--'
                    if not is_in_check(player_color, new_board):
                        return False  
    return True  

def is_stalemate(player_color, board):
    if is_in_check(player_color, board):
        return False
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece.startswith(player_color):
                valid_moves = get_valid_moves(piece, (row, col))
                if valid_moves:
                    return False
    return True

def threefoldrep():
    current_state = ''.join([''.join(row) for row in board]) + current_player
    occurrences = board_states.count(current_state)
    
    if occurrences >= 3:
        return True
    return False

def is_50_move():
    if half_move_counter >= 10:
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

def is_valid_move(piece, start, end, check_check=True):
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
        direction = -1
        if start_col == end_col and board[end_row][end_col] == '--':
            if end_row == start_row + direction:
                valid = True
            elif start_row == 6:
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

def get_valid_moves(piece, position):
    flipboard = invert(board) if player == 2 else board
    valid_moves = []
    for row in range(8):
        for col in range(8):
            if is_valid_move(piece, position, (row, col)):
                target_piece = flipboard[row][col]
                move_type = 'move' if target_piece == '--' else 'capture'
                valid_moves.append(((row, col), move_type))
    print(valid_moves)
    return valid_moves



### GAME FUNCTIONALITY

def wait_for_click():
    waiting = True
    while waiting:
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                waiting = False
    sys.exit()

def end_game(message):
    draw_endgame_message(message)
    wait_for_click()

def handle_click(pos):
    global selected_piece, selected_position, current_player, en_passant_target, castling_rights, valid_moves, half_move_counter
    board_x, board_y = [(screen.get_width() - 8 * SQUARE_SIZE) // 2, (screen.get_height() - 8 * SQUARE_SIZE) // 2]
    x, y = pos
    col = (x - board_x) // SQUARE_SIZE
    row = (y - board_y) // SQUARE_SIZE

    if 0 <= row < 8 and 0 <= col < 8:
        piece_at_square = board[row][col]
        
        if piece_at_square != '--' and piece_at_square[0] == current_player:
            selected_piece = piece_at_square
            selected_position = (row, col)
            valid_moves = get_valid_moves(selected_piece, selected_position)
        elif selected_piece:
            valid_move = is_valid_move(selected_piece, selected_position, (row, col))
            if valid_move:
                target_piece = board[row][col]  
                en_passant_capture = False
                if selected_piece[2:] == 'pawn' and (row, col) == en_passant_target:
                    en_passant_capture = True
                castling_move = False
                if selected_piece[2:] == 'king' and abs(selected_position[1] - col) == 2:
                    castling_move = True
                board[row][col] = selected_piece
                board[selected_position[0]][selected_position[1]] = '--'
                last_move[current_player] = (selected_position, (row, col))
                
                
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

                
                if selected_piece[2:] == 'king':
                    castling_rights[current_player]['K'] = False
                    castling_rights[current_player]['Q'] = False
                elif selected_piece[2:] == 'rook':
                    if selected_position[1] == 0:
                        castling_rights[current_player]['Q'] = False
                    elif selected_position[1] == 7:
                        castling_rights[current_player]['K'] = False

                
                opponent_color = 'b' if current_player == 'w' else 'w'
                store_board_state(board)
                

                if is_checkmate(opponent_color, board):
                    end_game(f"Checkmate! {'White' if opponent_color.capitalize() == 'W' else 'Black'} is checkmated. {'White' if opponent_color.capitalize() == 'B' else 'Black'} wins!")

                if is_stalemate(opponent_color, board):
                    end_game("Draw by stalemate!")

                if is_50_move():
                    end_game("Draw by 50-move rule!")
                
                if threefoldrep():
                    end_game("Draw by 3-fold repetition!")

                
                
                
                piece_type = selected_piece[2:]
                if piece_type == 'pawn' and abs(selected_position[0] - row) == 2:
                    en_passant_target = ((selected_position[0] + row) // 2, selected_position[1])
                else:
                    en_passant_target = None

            selected_piece = None
            selected_position = None
            valid_moves = []
            if player == 1:
                gref.child("board").set(board)
            else:
                gref.child("board").set(invert(board))
            current_player = 'b' if current_player == 'w' else 'w'
            gref.child("current_player").set(current_player)



### MAIN GAME LOOP

running = True
if player == 1:
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
                if current_player == 'w':
                    handle_click(event.pos)
        # print("JUST FINISHED EVENTSSSS NOW I RUN TIMER UPDATTTEEE")
        # update_timers()
        # print("JUST FINISH UPDATE TIMERS NOW IM GOING TO DRAW BOARDDDD")
        draw_board()
        # print("JUST FINISH DRAW BOARD NOW I DRAW PIECES")
        draw_pieces(board)
        # print("JUST DREW ALL THE SHIT NOW IM GONNA DRAW THE VALID MOVESS")
        draw_valid_moves()
        # print("JUST DREW ALL THE VALID MOVES NOW IM DRAWING THE TURN INDICATOR")
        draw_turn_indicator()
        # print("JUST DREW TURN INDICATOR NOW I DRAW TIMER")
        # draw_timers()
        # print("YAYYYYY ALL DONE NOW I DO BACKFLIP")
        pg.display.flip()
elif player == 2:
    while running:
        # print("IM GONNA RUN events!!!!")
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
                if current_player == 'b':
                    handle_click(event.pos)
        # print("JUST FINISHED EVENTSSSS NOW I RUN draw board")
        draw_board()
        # print("JUST FINISH DRAW BOARD NOW I DRAW PIECES")
        draw_pieces(board)
        # print("JUST DREW ALL THE SHIT NOW IM GONNA DRAW THE VALID MOVESS")
        draw_valid_moves()
        # print("JUST DREW ALL THE VALID MOVES NOW IM DRAWING THE TURN INDICATOR")
        draw_turn_indicator()
        # print("JUST DREW TURN INDICATOR NOW I DRAW TIMER")
        # draw_timers()
        # print("YAYYYYY ALL DONE NOW I DO BACKFLIP")
        pg.display.flip()


# Remove connections
if player == 1:
    whiteconn.set(False)
else:
    blackconn.set(False)

pg.quit()
sys.exit()
