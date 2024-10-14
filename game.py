import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up constants
# BOARD_MARGIN will be dynamically calculated later in the game loop based on screen size
BOARD_SIZE = 8
MIN_WIDTH, MIN_HEIGHT = 640, 480
screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
SQUARE_SIZE = int(screen.get_height() * 0.8) // BOARD_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (200, 165, 120)
DARK_BROWN = (120, 60, 40)

# Load background image
background = pygame.image.load('images/woodbackground.jpeg')
background = pygame.transform.smoothscale(background, (screen.get_width(), screen.get_height()))
pygame.display.set_caption('Simple Chess Game')

# Load piece images (assuming you have them in an 'images' folder)
original_pieces = {
    'b_king': pygame.image.load('images/b_king.png').convert_alpha(),
    'b_queen': pygame.image.load('images/b_queen.png').convert_alpha(),
    'b_rook': pygame.image.load('images/b_rook.png').convert_alpha(),
    'b_bishop': pygame.image.load('images/b_bishop.png').convert_alpha(),
    'b_knight': pygame.image.load('images/b_knight.png').convert_alpha(),
    'b_pawn': pygame.image.load('images/b_pawn.png').convert_alpha(),
    'w_king': pygame.image.load('images/w_king.png').convert_alpha(),
    'w_queen': pygame.image.load('images/w_queen.png').convert_alpha(),
    'w_rook': pygame.image.load('images/w_rook.png').convert_alpha(),
    'w_bishop': pygame.image.load('images/w_bishop.png').convert_alpha(),
    'w_knight': pygame.image.load('images/w_knight.png').convert_alpha(),
    'w_pawn': pygame.image.load('images/w_pawn.png').convert_alpha(),
}

# Create a copy for resized pieces
pieces = original_pieces.copy()

# Resize pieces to fit squares
BOARD_MARGIN = int(screen.get_height() * 0.1)
def resize_pieces():
    global SQUARE_SIZE, pieces
    SQUARE_SIZE = (min(screen.get_width(), screen.get_height()) - int(screen.get_height() * 0.1) * 2) // BOARD_SIZE
    for key in pieces:
        pieces[key] = pygame.transform.smoothscale(original_pieces[key], (SQUARE_SIZE, SQUARE_SIZE))

resize_pieces()

# Draw the chessboard
def draw_board():
    # Draw the background
    screen.blit(background, (0, 0))
    
    # Draw the chessboard centered on the background with a margin
    board_width = BOARD_SIZE * SQUARE_SIZE
    board_height = BOARD_SIZE * SQUARE_SIZE
    board_x = (screen.get_width() - board_width) // 2
    board_y = (screen.get_height() - board_height) // 2
    colors = [LIGHT_BROWN, DARK_BROWN]
    
    # Draw black border
    border_width = SQUARE_SIZE // 8
    border_rect = pygame.Rect(board_x - border_width, board_y - border_width, board_width + 2 * border_width, board_height + 2 * border_width)
    pygame.draw.rect(screen, BLACK, border_rect)
    
    # Draw squares
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, (board_x + col * SQUARE_SIZE, board_y + row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Draw pieces on the board
def draw_pieces(board):
    board_width = BOARD_SIZE * SQUARE_SIZE
    board_height = BOARD_SIZE * SQUARE_SIZE
    board_x = (screen.get_width() - board_width) // 2
    board_y = (screen.get_height() - board_height) // 2
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece != '--':
                screen.blit(pieces[piece], (board_x + col * SQUARE_SIZE, board_y + row * SQUARE_SIZE))

# Initial board state
def initial_board():
    return [
        ['b_rook', 'b_knight', 'b_bishop', 'b_queen', 'b_king', 'b_bishop', 'b_knight', 'b_rook'],
        ['b_pawn'] * 8,
        ['--'] * 8,
        ['--'] * 8,
        ['--'] * 8,
        ['--'] * 8,
        ['w_pawn'] * 8,
        ['w_rook', 'w_knight', 'w_bishop', 'w_queen', 'w_king', 'w_bishop', 'w_knight', 'w_rook']
    ]

board = initial_board()

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            new_width = max(event.w, MIN_WIDTH)
            new_height = max(event.h, MIN_HEIGHT)
            screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
            background = pygame.transform.smoothscale(pygame.image.load('images/woodbackground.jpeg'), (screen.get_width(), screen.get_height()))
            resize_pieces()

    # Draw everything
    draw_board()
    draw_pieces(board)

    # Update the display
    pygame.display.flip()

pygame.quit()
sys.exit()