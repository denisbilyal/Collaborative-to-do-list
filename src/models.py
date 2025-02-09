"""
This module defines the database models for a collaborative task management system.
It includes models for users, tables, tasks, tags, requests, and actions, as well as
enumerations for roles, task types, and priorities.
"""

from enum import Enum
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from . import db


class Role(Enum):
    """
    Enumeration representing the roles a user can have in a table.

    Attributes:
        REGULAR (0): A regular user with basic permissions.
        ADMIN (1): An admin user with additional administrative privileges.
        CREATOR (2): The creator of the table with full control over it.
    """
    REGULAR = 0
    ADMIN = 1
    CREATOR = 2


class TaskType(Enum):
    """
    Enumeration representing the types of tasks.

    Attributes:
        TO_DO (0): Tasks that are yet to be started.
        IN_PROGRESS (1): Tasks that are currently being worked on.
        COMPLETED (2): Tasks that have been completed.
    """
    TO_DO = 0
    IN_PROGRESS = 1
    COMPLETED = 2


class Priority(Enum):
    """
    Enumeration representing the priority levels of tasks.

    Attributes:
        LOW (0): Low priority tasks.
        MEDIUM (1): Medium priority tasks.
        HIGH (2): High priority tasks.
        URGENT (3): Urgent tasks requiring immediate attention.
    """
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    URGENT = 3


class User(db.Model, UserMixin):
    """
    Represents a user in the system.

    Attributes:
        id (int): The unique identifier for the user (primary key).
        username (str): The username of the user, must be unique.
        password (str): The hashed password of the user.
        tables (list[UserTable]): Relationships between the user and tables they belong to.
        received_requests (list[Request]): Requests received by the user.
    """
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    password: Mapped[str] = mapped_column()
    tables: Mapped[list['UserTable']] = relationship(back_populates='user')
    received_requests: Mapped[list['Request']] = relationship(foreign_keys='[Request.recipient_id]')

    def __repr__(self) -> str:
        return f'<User(id={self.id}, username={self.username})>'

    def __str__(self) -> str:
        return f'User: {self.username}'


class UserTable(db.Model):
    """
    Represents the many-to-many relationship between users and tables.

    Attributes:
        user_id (int): The ID of the user (foreign key to User).
        table_id (int): The ID of the table (foreign key to Table).
        role (Role): The role of the user in the table.
        user (User): Relationship to the User model.
        table (Table): Relationship to the Table model.
    """
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)
    table_id: Mapped[int] = mapped_column(ForeignKey('table.id'), primary_key=True)
    role: Mapped['Role'] = mapped_column()
    user: Mapped[list['User']] = relationship(back_populates='tables')
    table: Mapped[list['Table']] = relationship(back_populates='users')

    def __repr__(self) -> str:
        return f'<UserTable(user_id={self.user_id}, table_id={self.table_id}, role={self.role})>'

    def __str__(self) -> str:
        return f'UserTable: User ID {self.user_id} -> Table ID {self.table_id}, Role: {self.role}'


class Table(db.Model):
    """
    Represents a table in the system where tasks are managed.

    Attributes:
        id (int): The unique identifier for the table (primary key).
        table_name (str): The name of the table, must be unique.
        users (list[UserTable]): Users associated with this table.
        tags (list[Tag]): Tags associated with this table.
        tasks (list[Task]): Tasks within this table.
        actions (list[Action]): Actions logged for this table.
        requests (list[Request]): Requests related to this table.
    """
    id: Mapped[int] = mapped_column(primary_key=True)
    table_name: Mapped[str] = mapped_column(String(30), unique=True)
    users: Mapped[list['UserTable']] = relationship(back_populates='table',
                                                    cascade='all, delete-orphan')
    tags: Mapped[list['Tag']] = relationship(cascade='all, delete-orphan')
    tasks: Mapped[list['Task']] = relationship(cascade='all, delete-orphan')
    actions: Mapped[list['Action']] = relationship(cascade='all, delete-orphan')
    requests: Mapped[list['Request']] = relationship(cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'<Table(id={self.id}, name={self.table_name})>'

    def __str__(self) -> str:
        return f'Table: {self.table_name}'


class Request(db.Model):
    """
    Represents a request sent between users regarding a table.

    Attributes:
        sender_id (int): The ID of the sender (foreign key to User).
        recipient_id (int): The ID of the recipient (foreign key to User, part of primary key).
        table_id (int): The ID of the table (foreign key to Table, part of primary key).
        table (Table): Relationship to the Table model.
        sender (User): Relationship to the sender User model.
    """
    sender_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    recipient_id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)
    table_id: Mapped[int] = mapped_column(ForeignKey('table.id'), primary_key=True)
    table: Mapped['Table'] = relationship()
    sender: Mapped['User'] = relationship(foreign_keys='Request.sender_id')

    def __repr__(self) -> str:
        return (f'<Request(sender_id={self.sender_id},'
                f'recipient_id={self.recipient_id}, table_id={self.table_id})>')

    def __str__(self) -> str:
        return f'Request: From {self.sender_id} to {self.recipient_id} for Table {self.table_id}'


class Tag(db.Model):
    """
    Represents a tag that can be assigned to tasks.

    Attributes:
        id (int): The unique identifier for the tag (primary key).
        name (str): The name of the tag.
        table_id (int): The ID of the table the tag belongs to (foreign key to Table).
        tasks (list[Task]): Tasks associated with this tag.
    """
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(15))
    table_id: Mapped[int] = mapped_column(ForeignKey('table.id'))
    tasks: Mapped[list['Task']] = relationship(back_populates='tag')

    def __repr__(self) -> str:
        return f'<Tag(id={self.id}, name={self.name}, table_id={self.table_id})>'

    def __str__(self) -> str:
        return f'Tag: {self.name}'


class Task(db.Model):
    """
    Represents a task within a table.

    Attributes:
        id (int): The unique identifier for the task (primary key).
        title (str): The title of the task.
        description (str): The description of the task.
        priority (Priority): The priority level of the task.
        date (str): The creation date of the task.
        due_date (str): The due date of the task.
        type (TaskType): The type of the task (e.g., TO_DO, IN_PROGRESS, COMPLETED).
        tag_id (int): The ID of the tag assigned to the task (foreign key to Tag).
        user_id (int): The ID of the user assigned to the task (foreign key to User).
        table_id (int): The ID of the table the task belongs to (foreign key to Table).
        tag (Tag): Relationship to the Tag model.
        user (User): Relationship to the User model.
    """
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

    def __repr__(self) -> str:
        return (
            f'<Task(id={self.id}, title={self.title}, priority={self.priority}, '
            f'type={self.type}, due_date={self.due_date})>'
        )

    def __str__(self) -> str:
        return f'Task: {self.title} (Priority: {self.priority}, Due: {self.due_date})'


class Action(db.Model):
    """
    Represents an action logged in the system.

    Attributes:
        id (int): The unique identifier for the action (primary key).
        info (str): Information about the action.
        timestamp (str): The timestamp when the action was logged.
        user_id (int): The ID of the user who performed the action (foreign key to User).
        table_id (int): The ID of the table the action is related to (foreign key to Table).
        user (User): Relationship to the User model.
    """
    id: Mapped[int] = mapped_column(primary_key=True)
    info: Mapped[str] = mapped_column()
    timestamp: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    table_id: Mapped[int] = mapped_column(ForeignKey('table.id'))
    user: Mapped['User'] = relationship()

    def __repr__(self) -> str:
        return f'<Action(id={self.id}, info={self.info}, timestamp={self.timestamp})>'

    def __str__(self) -> str:
        return f'Action: {self.info} at {self.timestamp}'
