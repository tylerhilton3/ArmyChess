import json
import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase Admin SDK
cred = credentials.Certificate('client/firebaseprivatekey.json')  # Replace with your Service Account JSON path
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://army-chess-default-rtdb.firebaseio.com/'  # Replace with your Firebase Realtime Database URL
})

# Load JSON data from game.json


# Overwrite the database root with data from game.json
def dbinit():
    with open('client/game.json', 'r') as file:
        data = json.load(file)
    ref = db.reference('/')
    ref.set(data)

    print("Database initialized successfully!")

dbinit()