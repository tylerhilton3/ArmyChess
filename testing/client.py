import socket
import threading
import pickle

# Server configuration
HOST = '127.0.0.1'  # Localhost
PORT = 12345        # Server port

# Function to handle incoming messages from the server
def receive_messages(client_socket):
    while True:
        try:
            # Receive and deserialize message from the server
            message = pickle.loads(client_socket.recv(1024))
            print("\nReceived:", message)
        except EOFError:
            print("Disconnected from the server.")
            client_socket.close()
            break

# Main client function
def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    # Start a thread to listen for incoming messages
    thread = threading.Thread(target=receive_messages, args=(client_socket,))
    thread.start()

    # Main loop for sending messages
    while True:
        message = input("You: ")
        if message.lower() == 'exit':
            break
        
        # Serialize and send the message
        client_socket.sendall(pickle.dumps(message))
    
    client_socket.close()

if __name__ == "__main__":
    main()
