import socket
import pickle

# Client setup
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 5555))  # Server's IP and Port

while True:
    # Receiving data from the server
    try:
        message = client.recv(4096)  # Buffer size
        if not message:
            break  # If no message, the server likely disconnected
        message = pickle.loads(message)
        
        # Display the board (or any other data received)
        for row in message:
            print(row)
    except:
        break  # Handle any errors, e.g., server disconnects

client.close()
