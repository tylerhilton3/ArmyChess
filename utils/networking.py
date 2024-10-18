import pickle

def send_msg(conn, msg):
    data = pickle.dumps(msg)
    msg_length = len(data)
    
    # Print the serialized message and its length
    print(f"[SERVER SEND] Message Type: '{msg.get('type')}', Length: {msg_length}, Data: {data[:50]}...")  # Log first 50 bytes for debugging
    
    # Send the length and the serialized message
    conn.sendall(msg_length.to_bytes(4, byteorder='big') + data)


def recvall(conn, n):
    data = bytearray()
    
    # Print the expected number of bytes to receive
    print(f"[RECV] Expected to receive {n} bytes")

    while len(data) < n:
        packet = conn.recv(n - len(data))
        
        # If no data is received, print an error message
        if not packet:
            print("[ERROR] Socket connection broken or no more data")
            return None
        
        # Print the length of the received packet
        print(f"[RECV] Received packet of length {len(packet)}")
        
        data.extend(packet)
    
    # Print the total length of the received data
    print(f"[RECV] Total data received: {len(data)} bytes")
    return data

def recv_msg(conn):
    # Receive the length of the incoming message (4 bytes)
    raw_msglen = recvall(conn, 4)
    if not raw_msglen:
        print("[ERROR] No message length received")
        return None

    msglen = int.from_bytes(raw_msglen, byteorder='big')
    print(f"[CLIENT RECV] Message length expected: {msglen}")
    
    # Now receive the actual message data of 'msglen' bytes
    msg_data = recvall(conn, msglen)
    if not msg_data:
        print("[ERROR] No message data received")
        return None

    print(f"[CLIENT RECV] Message data of length {len(msg_data)} received")
    
    # Deserialize the received data using pickle
    try:
        message = pickle.loads(msg_data)
        print(f"[CLIENT RECV] Message Type: '{message.get('type')}' successfully deserialized")
        return message
    except Exception as e:
        print(f"[ERROR] pickle.loads failed: {e}")
        print(f"[ERROR] msg_data: {msg_data}")
        raise
