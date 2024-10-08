from tinydb import TinyDB, Query
import os

DB_FILE = os.path.join(os.path.dirname(__file__), 'db.json')

db = TinyDB(DB_FILE)