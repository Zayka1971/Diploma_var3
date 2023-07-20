from sqlalchemy import create_engine, Column, Integer, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import config

# Создание подключения к базе данных
engine = create_engine(url=config.db_url_object)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class Profile(Base):
    # __table_args__ = {'schema': 'vk_api'}
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    offset = Column(Integer, default=0)


class Viewed(Base):
    # __table_args__ = {'schema': 'vk_api'}
    __tablename__ = 'viewed'
    profile_id = Column(Integer, primary_key=True)
    worksheet_id = Column(Integer, primary_key=True)


def create_user(user_id, offset=0):
    try:
        user = Profile(id=user_id, offset=offset)
        session.add(user)
        session.flush()
        return user
    except Exception as exc:
        print(exc)
        print(f'User {user_id} already exists')


def create_view(profile_id, worksheet_id):
    try:
        view = Viewed(profile_id=profile_id, worksheet_id=worksheet_id)
        session.add(view)
        session.flush()
        return view
    except Exception as exc:
        print(exc)
        print(f'View already exists')


def get_view(profile_id, worksheet_id):
    query = select(Viewed).where(Viewed.profile_id == profile_id, Viewed.worksheet_id == worksheet_id)
    return session.scalar(query)


def get_user_by_id(user_id):
    query = select(Profile).where(Profile.id == user_id)
    return session.scalar(query)


def update_user(user_id, offset=None):
    user = session.query(Profile).get(user_id)
    user.offset = offset
    session.commit()
    return user


Base.metadata.create_all(engine)
