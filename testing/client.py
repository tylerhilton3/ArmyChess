import firebase_admin
from firebase_admin import credentials, db
import threading
import time

# Firebase initialization
cred = credentials.Certificate("testing/firebaseprivatekey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://army-chess-default-rtdb.firebaseio.com/'
})

# Game settings
game_ref = db.reference('games/game1')
client_id = None
game_ref.child('players').delete()

def initialize_client():
    global client_id
    players_ref = game_ref.child('players')

    # Use a transaction to ensure atomic assignment of player slots
    def assign_player_slot(current_data):
        global client_id
        if not current_data:
            # No players yet, assign as player1
            client_id = 'player1'
            return {'player1': True}
        elif 'player1' in current_data and 'player2' not in current_data:
            # player1 exists, assign as player2
            client_id = 'player2'
            current_data['player2'] = True
            return current_data
        elif 'player1' not in current_data:
            # Assign player1 if only player2 exists
            client_id = 'player1'
            current_data['player1'] = True
            return current_data
        else:
            # Both players are already assigned
            print("Game is full. Only two players can join.")
            return None

    # Run the transaction
    players_ref.transaction(assign_player_slot)

    # Check if the client was assigned a player slot
    if client_id is None:
        exit(1)  # Exit if the game is full

    print(f"You are {client_id}. Waiting for the other player to join...")

    # Wait until both players are present
    while players_ref.get().get('player2') is None:
        time.sleep(1)

    print("Both players are connected. Game is starting!")

def game_loop():
    """Main game loop for turn-based messaging."""
    while True:
        game_state = game_ref.get()
        turn = game_state.get('turn')
        message_count = game_state.get('message_count', 0)

        if message_count >= 10:
            print("Game over! Both players sent 5 messages.")
            break

        # Check if it's the client's turn
        if turn == client_id:
            print("It's your turn. Enter a message:")
            message = input("Message: ")
            game_ref.child('messages').push({
                'from': client_id,
                'text': message
            })

            # Update the game state for the next turn
            game_ref.update({
                'turn': 'player2' if client_id == 'player1' else 'player1',
                'message_count': message_count + 1
            })

        else:
            # Wait for the other player to take their turn
            print("Waiting for the other player's turn...")
            time.sleep(2)  # Poll every 2 seconds

def main():
    initialize_client()
    game_loop()

if __name__ == "__main__":
    main()