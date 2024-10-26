import socket
import threading
import pickle

# Server configuration
HOST = '127.0.0.1'  # Localhost
PORT = 12345        # Port to listen on

# Maintain a list of connected clients
clients = []

# Broadcast message to all connected clients except the source client
def broadcast(message, source_client):
    for client in clients:
        if client != source_client:
            try:
                client.sendall(pickle.dumps(message))
            except:
                clients.remove(client)

# Handle each client's messages
def handle_client(client_socket):
    while True:
        try:
            # Receive and deserialize message from the client
            message = pickle.loads(client_socket.recv(1024))
            print(f"Received message: {message}")
            
            # Broadcast the message to other clients
            broadcast(message, client_socket)
        except (EOFError, ConnectionResetError):
            print("A client has disconnected.")
            clients.remove(client_socket)
            client_socket.close()
            break

# Main server setup
def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"Server listening on {HOST}:{PORT}")
    
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connected by {addr}")
        clients.append(client_socket)
        
        # Start a new thread for each client connection
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

if __name__ == "__main__":
    main()
