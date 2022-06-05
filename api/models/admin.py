from sqlalchemy import Column, Integer, String, Boolean
from database.db_config import Base, session
from werkzeug.security import check_password_hash, generate_password_hash

class Admin(Base):
    __tablename__ = 'administrators'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __repr__(self):
        return '<Admin %r>' % self.email

    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'password': self.password,
        }

    def generate_password(self):
        self.password = generate_password_hash(self.password, method='sha256')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def find_by_email(email):
        return session.query(Admin).filter_by(email=email).first()

    def find_by_id(id):
        return session.query(Admin).filter_by(id=id).first()

    def add_admin(self):
        session.add(self)
        session.commit()

    def delete_admin(self):
        session.delete(self)
        session.commit()
