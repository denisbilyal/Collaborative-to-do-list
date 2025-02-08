from enum import Enum

from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey

from . import db

class Role(Enum):
    REGULAR = 0
    ADMIN = 1
    CREATOR = 2

class TaskType(Enum):
    TO_DO = 0
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

    received_requests: Mapped[list['Request']] = relationship(foreign_keys="[Request.recipient_id]")

class UserTable(db.Model):
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)
    table_id: Mapped[int] = mapped_column(ForeignKey('table.id'), primary_key=True)
    role: Mapped['Role'] = mapped_column()

    user: Mapped[list['User']] = relationship(back_populates='tables')
    table: Mapped[list['Table']] = relationship(back_populates='users')

class Table(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    table_name: Mapped[str] = mapped_column(String(30), unique=True)

    users: Mapped[list['UserTable']] = relationship(back_populates='table',
                                                     cascade='all, delete-orphan')
    tags: Mapped[list['Tag']] = relationship(cascade='all, delete-orphan')
    tasks: Mapped[list['Task']] = relationship(cascade='all, delete-orphan')
    actions: Mapped[list['Action']] = relationship(cascade='all, delete-orphan')
    requests: Mapped[list['Request']] = relationship(cascade='all, delete-orphan')

class Request(db.Model):
    sender_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    recipient_id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)
    table_id: Mapped[int] = mapped_column(ForeignKey('table.id'), primary_key=True)

    table: Mapped['Table'] = relationship()
    sender: Mapped['User'] = relationship(foreign_keys=sender_id)

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
