from app import db, app  # import both db and Flask app

with app.app_context():   # set app context
    db.drop_all()         # drop all tables
    db.create_all()       # recreate tables

print("Database reset complete!")
