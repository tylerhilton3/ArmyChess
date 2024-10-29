import json
import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate('client/firebaseprivatekey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://army-chess-default-rtdb.firebaseio.com/'
})


def dbinit():
    with open('client/game.json', 'r') as file:
        data = json.load(file)
    ref = db.reference('/')
    ref.set(data)

    print("Database initialized successfully!")

dbinit()