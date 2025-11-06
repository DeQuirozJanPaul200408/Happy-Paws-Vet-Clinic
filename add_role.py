from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import pymysql

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/vetclinic'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Connect to DB and add column
with app.app_context():
    # Check if the 'role' column already exists
    check_query = text("SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'user' AND column_name = 'role'")
    result = db.session.execute(check_query).scalar()
    if result == 0:
        db.session.execute(text("ALTER TABLE `user` ADD COLUMN role VARCHAR(20) DEFAULT 'user'"))
        db.session.commit()
        print("Role column added to user table.")
    else:
        print("Role column already exists in user table.")
