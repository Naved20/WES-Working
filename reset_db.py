from app import db, app  # import both db and Flask app
from app import MasterTask

with app.app_context():   # set app context
    db.drop_all()         # drop all tables
    db.create_all()       # recreate tables

print("Database reset complete!")
