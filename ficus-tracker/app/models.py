from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import uuid


class FicusTrackerUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    token = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def generate_token():
        return uuid.uuid4()

    def __repr__(self):
        return '<User {}>'.format(self.login)
