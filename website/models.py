from enum import Enum

from . import db

from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey


class Role(Enum):
    REGULAR = 0
    ADMIN = 1
    CREATOR = 2

class TaskType(Enum):
    UNSTARTED = 0
    IN_PROGRESS = 1
    COMPLETED = 2

class Priority(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    URGENT = 3

class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    password: Mapped[str] = mapped_column()

    tables: Mapped[list['UserTable']] = relationship(back_populates='user')

class UserTable(db.Model):
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)
    table_id: Mapped[int] = mapped_column(ForeignKey('table.id'), primary_key=True)
    role: Mapped['Role'] = mapped_column()

    user: Mapped[list['User']] = relationship(back_populates='tables')
    table: Mapped[list['Table']] = relationship(back_populates='users')

class Table(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    table_name: Mapped[str] = mapped_column(String(30), unique=True)

    users: Mapped[list['UserTable']] = relationship(back_populates='table')
    tags: Mapped[list['Tag']] = relationship()
    tasks: Mapped[list['Task']] = relationship()
    actions: Mapped[list['Action']] = relationship()

class Request(db.Model):
    sender_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    recipient_id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)
    table_id: Mapped[int] = mapped_column(ForeignKey('table.id'), primary_key=True)

class Tag(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(15))
    table_id: Mapped[int] = mapped_column(ForeignKey('table.id'))

    tasks: Mapped[list['Task']] = relationship(back_populates='tag')


class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column()
    priority: Mapped['Priority'] = mapped_column()
    date: Mapped[str] = mapped_column()
    due_date: Mapped[str] = mapped_column()
    type: Mapped['TaskType'] = mapped_column()
    tag_id: Mapped[int] = mapped_column(ForeignKey('tag.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    table_id: Mapped[int] = mapped_column(ForeignKey('table.id'))

    tag: Mapped['Tag'] = relationship(back_populates='tasks')
    user: Mapped['User'] = relationship()

class Action(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    info: Mapped[str] = mapped_column()
    timestamp: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    table_id: Mapped[int] = mapped_column(ForeignKey('table.id'))

    user: Mapped['User'] = relationship()

