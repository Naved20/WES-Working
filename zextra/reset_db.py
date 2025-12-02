# reset_db.py
from app import db, app  # import both db and Flask app
from app import MasterTask

with app.app_context():   # set app context
    db.session.query(MasterTask).delete()
    db.session.commit()  
    
    print("MasterTask table records deleted!")

print("Database reset complete!")