import pygame as pg
import sys
import os
import firebase_admin
from firebase_admin import credentials, db
import time as t
import json

cred = credentials.Certificate("client/firebaseprivatekey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://army-chess-default-rtdb.firebaseio.com/'
})

pee = db.reference("players").get()
print(bool(pee))