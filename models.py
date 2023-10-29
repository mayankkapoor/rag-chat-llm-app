import os
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

server = os.environ.get("POSTGRES_SERVER")
username = os.environ.get("POSTGRES_USER")
password = os.environ.get("POSTGRES_PASSWORD")
database = os.environ.get("POSTGRES_DB")
db_port = os.environ.get("DB_PORT", default=5432)

# DB config
DATABASE_URI = f"postgresql://{username}:{password}@{server}:{db_port}/{database}"
DATABASE_URI_DOCKER = f"postgres://{username}:{password}@{server}:{db_port}/{database}"

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["DATABASE_URI"] = DATABASE_URI_DOCKER

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(), nullable=False)
    answer = db.Column(db.String(), nullable=False)
