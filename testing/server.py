import socket
import pickle
import threading

# Initialize and configure server to use IPv4 and TCP, binding to localhost on port 5555
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 5555))
server.listen(2)  # Allow up to 2 clients to wait in the connection queue

# List to keep track of connected clients
clients = []

# Function to send data to all connected clients
def broadcast(data):
    message = pickle.dumps(data)  # Serialize the data for transmission
    for client in clients:
        try:
            client.send(message)  # Send data to each client
        except:
            clients.remove(client)  # Remove client if sending fails

# Function to handle communication with a connected client
def handle_client(client_socket, client_address):
    print(f"Connection from {client_address} established!")
    clients.append(client_socket)  # Add new client to list
    
    print(f"There are {len(clients)} clients connected: {clients}")

    # Set up initial chess board layout
    board_state = [['b_rook', 'b_knight', 'b_bishop', 'b_queen', 'b_king', 'b_bishop', 'b_knight', 'b_rook'],
                   ['b_pawn'] * 8,
                   ['--'] * 8, ['--'] * 8,
                   ['--'] * 8, ['--'] * 8,
                   ['w_pawn'] * 8,
                   ['w_rook', 'w_knight', 'w_bishop', 'w_queen', 'w_king', 'w_bishop', 'w_knight', 'w_rook']]

    # Broadcast the initial board state to the newly connected client
    broadcast(board_state)

    while True:
        try:
            data = client_socket.recv(4096)  # Receive data from client
            if not data:
                break  # Exit if no data is received (client disconnected)

            # Broadcast received data (e.g., moves) to all clients
            broadcast(pickle.loads(data))
        except:
            break  # Exit loop on any error (e.g., client disconnection)

    print(f"Connection with {client_address} closed.")
    clients.remove(client_socket)  # Remove client from list
    print(f"There are {len(clients)} clients connected: {clients}")
    client_socket.close()  # Close the client connection"

# Main server loop to accept and manage multiple client connections
while True:
    client_socket, client_address = server.accept()  # Accept new client connection
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()  # Start a new thread to handle the connected client
