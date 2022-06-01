import datetime
from enum import unique
import sqlalchemy
from db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)
    sid = sqlalchemy.Column(sqlalchemy.String,
                           unique=True, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, 
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    achievements = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    playing_time = sqlalchemy.Column(sqlalchemy.Float, default=0.0)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, 
                                     default=datetime.datetime.now)
    