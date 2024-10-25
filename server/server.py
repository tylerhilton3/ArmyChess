import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import socket
import threading
from ..utils.networking import send_msg, recv_msg

# Server settings
HOST = '127.0.0.1'
PORT = 65432

# Global game state
game_state = {
    'board': [
        ['b_rook', 'b_knight', 'b_bishop', 'b_queen', 'b_king', 'b_bishop', 'b_knight', 'b_rook'],
        ['b_pawn'] * 8,
        ['--'] * 8, ['--'] * 8, ['--'] * 8, ['--'] * 8,
        ['w_pawn'] * 8,
        ['w_rook', 'w_knight', 'w_bishop', 'w_queen', 'w_king', 'w_bishop', 'w_knight', 'w_rook']
    ],
    'last_move': None,
    'current_turn': 'w',
}

clients = []

def broadcast_game_state():
    global game_state
    for client in clients:
        try:
            send_msg(client['conn'], {'type': 'game_state', 'data': game_state})
        except:
            print("Error sending game state to a client.")

def handle_client(conn, addr):
    global game_state, clients
    print(f"Connected to {addr}")

    # Assign a color to the client
    if len(clients) == 0:
        player_color = 'w'
    elif len(clients) == 1:
        player_color = 'b'
    else:
        # Reject additional clients
        send_msg(conn, {'type': 'error', 'message': 'Game is full.'})
        conn.close()
        return

    # Add client to the list with assigned color
    clients.append({'conn': conn, 'addr': addr, 'color': player_color})

    send_msg(conn, {'type': 'color', 'color': player_color})
    send_msg(conn, {'type': 'game_state', 'data': game_state})

    while True:
        try:
            move_data = recv_msg(conn)
            if not move_data:
                print(f"Client {addr} disconnected.")
                break

            if move_data['type'] == 'move':
                # Update the game state
                game_state['board'] = move_data['board']
                game_state['last_move'] = move_data['last_move']
                game_state['current_turn'] = 'b' if move_data['player'] == 'w' else 'w'

                # Broadcast the updated game state
                broadcast_game_state()
            else:
                print("Unknown data type received from client.")

        except Exception as e:
            print(f"Connection error with {addr}: {e}")
            break

    # Remove client from the list
    conn.close()
    clients = [c for c in clients if c['conn'] != conn]
    print(f"Disconnected from {addr}")


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(2)
        print(f"Server started on {HOST}:{PORT}. Waiting for players to connect...")

        while True:
            conn, addr = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()

if __name__ == "__main__":
    start_server()
