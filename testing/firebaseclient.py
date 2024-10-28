import firebase_admin
from firebase_admin import credentials, db
import time as t

cred = credentials.Certificate("testing/firebaseprivatekey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://army-chess-default-rtdb.firebaseio.com/'
})


game_id = 'game1'

game = db.reference(f'/games/{game_id}')
whiteconn = db.reference(f"games/{game_id}/connections/white")
blackconn = db.reference(f"games/{game_id}/connections/black")

blackconnected = False

def wait_for_connection(event):
    global blackconnected
    if event.data == True:
        print("Player 2 has connected!")
        blackconnected = True


# Player assignment
if not whiteconn.get():
    player = 1
    opp = 2
    print(f"You are player 1.")
    whiteconn.set(True)
    p2listener = blackconn.listen(wait_for_connection)
    while not blackconnected:
        t.sleep(1.5)
        print("Waiting for player 2...")
    p2listener.close()
else:
    player = 2
    opp = 1
    print("You are player 2.")
    blackconn.set(True)
    blackconnected = True

