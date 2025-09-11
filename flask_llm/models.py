from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """Required by Flask-Login"""
        return str(self.id)

    def __repr__(self):
        return f"<User {self.username}>"
    

class Counter(db.Model):
    __tablename__ = "counters"
    __table_args__ = (db.UniqueConstraint("user_id", "date", name="uq_user_date_counter"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    date = db.Column(db.Date, default=datetime.utcnow().date, nullable=False)
    count = db.Column(db.Integer, default=0, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("counter", uselist=False))

    @classmethod
    def increment(cls, user_id: int):
        today = datetime.utcnow().date()
        counter = cls.query.filter_by(user_id=user_id, date=today).first()

        if not counter:
            counter = cls(user_id=user_id, date=today, count=1)
            db.session.add(counter)
        else:
            counter.count += 1
            counter.updated_at = datetime.utcnow()

        db.session.commit()
        return counter

