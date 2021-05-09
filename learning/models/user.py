import bcrypt
from sqlalchemy import (Column, Integer, Text)
from .meta import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    role = Column(Text, nullable=False)
    password_hash = Column(Text)

    def set_password(self, pwd):
        hash = bcrypt.hashpw(pwd.encode('utf8'), bcrypt.gensalt())
        self.password_hash = hash.decode('utf8')

    def check_password(self, pwd):
        if self.password_hash is None:
            return False
        expected = self.password_hash.encode('utf8')
        return bcrypt.checkpw(pwd.encode('utf8'), expected)
