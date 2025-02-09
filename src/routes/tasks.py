"""
Tasks Module

This module handles task-related functionality for tables, including displaying tasks,
creating new tasks, starting, finishing, rejecting, undoing, and clearing tasks. It also
handles real-time updates using WebSockets.

Routes:
    - `/tables/<int:table_id>`: Displays the list of tasks for a specific table.
    - `/tables/<int:table_id>/create-task`: Handles the creation of a new task.
    - `/tables/<int:table_id>/start-task`: Handles marking a task as 'in progress.'
    - `/tables/<int:table_id>/delete-task`: Handles deleting a task.
    - `/tables/<int:table_id>/reject-task`: Handles rejecting a task (moving it back to 'to do').
    - `/tables/<int:table_id>/finish-task`: Handles marking a task as 'completed.'
    - `/tables/<int:table_id>/undo-task`: Handles moving a completed task back to 'in progress.'
    - `/tables/<int:table_id>/clear-task`: Handles clearing a task (deleting it).

Attributes:
    - tasks_bp: The Flask Blueprint for task-related routes.

Functions:
    - on_join_room: Handles WebSocket room joins for real-time updates.
    - get_tasks: Fetches tasks grouped by their type (to do, in progress, completed).
    - emit_changes: Emits updated task data to all clients in the table's WebSocket room.
    - task_to_dict: Converts a Task object into a dictionary for JSON serialization.
"""

from datetime import date
from typing import Any
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_socketio import join_room
from werkzeug.wrappers import Response
from src import db, socketio
from ..models import Table, UserTable, Priority, Task, TaskType
from .activity import save_action


@socketio.on('join_room')
def on_join_room(room_name: str) -> None:
    """
    Handles WebSocket room joins for real-time updates.

    Args:
        room_name (str): The name of the room to join (e.g., 'table_<table_id>').

    Returns:
        None
    """
    join_room(room_name)

def get_tasks(table_id: int) -> tuple[list[dict[str, Any]],
                                      list[dict[str, Any]],
                                      list[dict[str, Any]]]:
    """
    Fetches tasks grouped by their type (to do, in progress, completed).

    Args:
        table_id (int): The ID of the table whose tasks are being fetched.

    Returns:
        tuple: Three lists of tasks as dictionaries:
            - tasks_to_do: Tasks in the 'to do' state.
            - tasks_progress: Tasks in the 'in progress' state.
            - tasks_finished: Tasks in the 'completed' state.
    """
    tasks_to_do = [task_to_dict(task) for task in
                   list(Task.query.filter_by(table_id=table_id, type=TaskType.TO_DO))]
    tasks_progress = [task_to_dict(task) for task in
                      list(Task.query.filter_by(table_id=table_id, type=TaskType.IN_PROGRESS))]
    tasks_finished = [task_to_dict(task) for task in
                      list(Task.query.filter_by(table_id=table_id, type=TaskType.COMPLETED))]
    return tasks_to_do, tasks_progress, tasks_finished


def emit_changes(table_id: int) -> None:
    """
    Emits updated task data to all clients in the table's WebSocket room.

    Args:
        table_id (int): The ID of the table whose tasks are being updated.

    Returns:
        None
    """
    tasks_to_do, tasks_progress, tasks_finished = get_tasks(table_id)
    socketio.emit('update_tasks', {
        'tasks_to_do': tasks_to_do,
        'tasks_progress': tasks_progress,
        'tasks_finished': tasks_finished
    }, room=f'table_{table_id}')


def task_to_dict(task: Task) -> dict[str, Any]:
    """
    Converts a Task object into a dictionary for JSON serialization.

    Args:
        task (Task): The Task object to convert.

    Returns:
        dict: A dictionary representation of the Task object.
    """
    return {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'tag': {'name': task.tag.name} if task.tag else None,
        'priority': {'name': task.priority.name} if task.priority else None,
        'user': {'username': task.user.username} if task.user else None,
        'due_date': f'{task.due_date[8:10]}/{task.due_date[5:7]}/{task.due_date[0:4]}'
        if task.due_date else None,
        'date': f'{task.date[8:10]}/{task.date[5:7]}/{task.date[0:4]}'
        if task.date else None
    }


tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/tables/<int:table_id>')
@login_required
def tasks(table_id: int) -> str:
    """
    Displays the list of tasks for a specific table.

    This route fetches the tasks, tags, and priorities for the specified table and renders
    the 'tasks.html' template with this information.

    Args:
        table_id (int): The ID of the table whose tasks are being viewed.

    Returns:
        str: The rendered 'tasks.html' template.
    """
    table = db.get_or_404(Table, table_id)
    user_id = current_user.id
    db.get_or_404(UserTable, [user_id, table_id])

    tasks_to_do, tasks_progress, tasks_finished = get_tasks(table_id)

    return render_template(
        'tasks.html',
        user=current_user,
        table=table,
        priorities=Priority,
        tasks_to_do=tasks_to_do,
        tasks_progress=tasks_progress,
        tasks_finished=tasks_finished,
        user_id=current_user.id
    )


@tasks_bp.route('/tables/<int:table_id>/create-task', methods=['POST'])
@login_required
def create_task(table_id: int) -> Response:
    """
    Handles the creation of a new task.

    This route processes the form submission for creating a new task. If the input is valid,
    the task is created, and changes are emitted to the WebSocket room.

    Args:
        table_id (int): The ID of the table where the task will be created.

    Returns:
        Response: Redirects to the tasks page for the specified table.
    """
    if request.method == 'POST':
        title = request.form['task_name']
        description = request.form['task_description']
        tag_id = request.form.get('tag_id')
        priority = request.form['priority']
        due_date = request.form['due_date']

        if tag_id is None:
            flash('Cannot create task without a tag.', 'error')
            return redirect(url_for('tasks.tasks', table_id=table_id))

        if due_date == '':
            flash('Invalid due date.', 'error')
            return redirect(url_for('tasks.tasks', table_id=table_id))

        # Create the new task
        task = Task(
            title=title,
            description=description,
            priority=priority,
            date=date.today().strftime('%Y-%m-%d'),
            due_date=due_date,
            type=TaskType.TO_DO,
            tag_id=tag_id,
            user_id=current_user.id,
            table_id=table_id
        )
        db.session.add(task)
        save_action(current_user.id, table_id, f'Created a task: {task.title}')
        db.session.commit()
        emit_changes(table_id)

    return redirect(url_for('tasks.tasks', table_id=table_id))


@tasks_bp.route('/tables/<int:table_id>/start-task', methods=['POST'])
@login_required
def start_task(table_id: int) -> Response:
    """
    Handles marking a task as 'in progress.'

    This route updates the task's type to 'in progress' and assigns it to the current user.

    Args:
        table_id (int): The ID of the table containing the task.

    Returns:
        Response: Redirects to the tasks page for the specified table.
    """
    if request.method == 'POST':
        task_id = request.form['task_id']
        task = db.get_or_404(Task, task_id)
        task.type = TaskType.IN_PROGRESS
        task.user_id = current_user.id
        db.session.commit()
        emit_changes(table_id)

    return redirect(url_for('tasks.tasks', table_id=table_id))


@tasks_bp.route('/tables/<int:table_id>/delete-task', methods=['POST'])
@login_required
def delete_task(table_id: int) -> Response:
    """
    Handles deleting a task.

    This route deletes the specified task and emits updates to the WebSocket room.

    Args:
        table_id (int): The ID of the table containing the task.

    Returns:
        Response: Redirects to the tasks page for the specified table.
    """
    if request.method == 'POST':
        task_id = request.form['task_id']
        task = db.get_or_404(Task, task_id)
        db.session.delete(task)
        save_action(current_user.id, table_id, f'Deleted a task: {task.title}')
        db.session.commit()
        emit_changes(table_id)

    return redirect(url_for('tasks.tasks', table_id=table_id))


@tasks_bp.route('/tables/<int:table_id>/reject-task', methods=['POST'])
@login_required
def reject_task(table_id: int) -> Response:
    """
    Handles rejecting a task (moving it back to 'to do').

    This route updates the task's type to 'to do.'

    Args:
        table_id (int): The ID of the table containing the task.

    Returns:
        Response: Redirects to the tasks page for the specified table.
    """
    if request.method == 'POST':
        task_id = request.form['task_id']
        task = db.get_or_404(Task, task_id)
        task.type = TaskType.TO_DO
        db.session.commit()
        emit_changes(table_id)

    return redirect(url_for('tasks.tasks', table_id=table_id))


@tasks_bp.route('/tables/<int:table_id>/finish-task', methods=['POST'])
@login_required
def finish_task(table_id: int) -> Response:
    """
    Handles marking a task as 'completed.'

    This route updates the task's type to 'completed' and sets the completion date.

    Args:
        table_id (int): The ID of the table containing the task.

    Returns:
        Response: Redirects to the tasks page for the specified table.
    """
    if request.method == 'POST':
        task_id = request.form['task_id']
        task = db.get_or_404(Task, task_id)
        task.type = TaskType.COMPLETED
        task.date = date.today().strftime('%Y-%m-%d')  # Set the completion date
        db.session.commit()
        emit_changes(table_id)

    return redirect(url_for('tasks.tasks', table_id=table_id))


@tasks_bp.route('/tables/<int:table_id>/undo-task', methods=['POST'])
@login_required
def undo_task(table_id: int) -> Response:
    """
    Handles moving a completed task back to 'in progress.'

    This route updates the task's type to 'in progress.'

    Args:
        table_id (int): The ID of the table containing the task.

    Returns:
        Response: Redirects to the tasks page for the specified table.
    """
    if request.method == 'POST':
        task_id = request.form['task_id']
        task = db.get_or_404(Task, task_id)
        task.type = TaskType.IN_PROGRESS
        db.session.commit()
        emit_changes(table_id)

    return redirect(url_for('tasks.tasks', table_id=table_id))


@tasks_bp.route('/tables/<int:table_id>/clear-task', methods=['POST'])
@login_required
def clear_task(table_id: int) -> Response:
    """
    Handles clearing a task (deleting it).

    This route deletes the specified task and emits updates to the WebSocket room.

    Args:
        table_id (int): The ID of the table containing the task.

    Returns:
        Response: Redirects to the tasks page for the specified table.
    """
    if request.method == 'POST':
        task_id = request.form['task_id']
        task = db.get_or_404(Task, task_id)
        db.session.delete(task)
        db.session.commit()
        emit_changes(table_id)

    return redirect(url_for('tasks.tasks', table_id=table_id))
