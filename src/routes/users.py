"""
Users Module

This module handles user-related functionality for tables, including displaying users,
inviting new users, promoting or demoting users, and kicking users from a table.

Routes:
    - `/tables/<int:table_id>/users`: Displays the list of users in a specific table.
    - `/tables/<int:table_id>/invite-user`: Handles inviting a new user to the table.
    - `/tables/<int:table_id>/promote-user`: Handles promoting a user to the admin role.
    - `/tables/<int:table_id>/demote-user`: Handles demoting a user to the regular role.
    - `/tables/<int:table_id>/kick-user`: Handles removing a user from the table.

Attributes:
    - users_bp: The Flask Blueprint for user-related routes.

Functions:
    - users: Renders the list of users in a specific table.
    - invite_user: Invites a new user to the specified table.
    - promote_user: Promotes a user to the admin role.
    - demote_user: Demotes a user to the regular role.
    - kick_user: Removes a user from the table and updates their tasks.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.wrappers import Response
from src import db
from ..models import Table, UserTable, User, Request, Task, TaskType, Role
from .activity import save_action

users_bp = Blueprint('users', __name__)


@users_bp.route('/tables/<int:table_id>/users')
@login_required
def users(table_id: int) -> str:
    """
    Displays the list of users in a specific table.

    This route fetches the table, ensures the current user has access, and retrieves all
    users associated with the table. It also determines the current user's role in the table.

    Args:
        table_id (int): The ID of the table whose users are being viewed.

    Returns:
        str: The rendered 'users.html' template.
    """
    table = db.get_or_404(Table, table_id)
    user_id = current_user.id
    db.get_or_404(UserTable, [user_id, table_id])

    users_in_table = UserTable.query.filter_by(table_id=table_id)
    user_table = db.get_or_404(UserTable, [user_id, table_id])
    role = user_table.role

    return render_template(
        'users.html',
        user=current_user,
        table=table,
        users_in_table=users_in_table,
        role=role
    )


@users_bp.route('/tables/<int:table_id>/invite-user', methods=['POST'])
@login_required
def invite_user(table_id: int) -> Response:
    """
    Handles inviting a new user to the specified table.

    This route processes the form submission for inviting a user. If the user exists and
    is not already in the table or invited, an invitation is sent.

    Args:
        table_id (int): The ID of the table where the user is being invited.

    Returns:
        Response: Redirects to the users page for the specified table.
    """
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()

        if user is None:
            flash('This user does not exist.', 'error')
            return redirect(url_for('users.users', table_id=table_id))

        user_table = UserTable.query.filter_by(user_id=user.id, table_id=table_id).first()
        if user_table is not None:
            flash('This user is already in the table.', 'error')
            return redirect(url_for('users.users', table_id=table_id))

        invite = Request.query.filter_by(recipient_id=user.id, table_id=table_id).first()
        if invite:
            flash('This user is already invited.', 'error')
            return redirect(url_for('users.users', table_id=table_id))

        invite = Request(sender_id=current_user.id, recipient_id=user.id, table_id=table_id)
        db.session.add(invite)
        db.session.commit()
        flash('User successfully invited.')

    return redirect(url_for('users.users', table_id=table_id))


@users_bp.route('/tables/<int:table_id>/promote-user', methods=['POST'])
@login_required
def promote_user(table_id: int) -> Response:
    """
    Handles promoting a user to the admin role.

    This route promotes the specified user to the admin role in the table.

    Args:
        table_id (int): The ID of the table where the user is being promoted.

    Returns:
        Response: Redirects to the users page for the specified table.
    """
    if request.method == 'POST':
        user_id = request.form['user_id']
        user = db.get_or_404(UserTable, [user_id, table_id])
        user.role = Role.ADMIN
        db.session.commit()

    return redirect(url_for('users.users', table_id=table_id))


@users_bp.route('/tables/<int:table_id>/demote-user', methods=['POST'])
@login_required
def demote_user(table_id: int) -> Response:
    """
    Handles demoting a user to the regular role.

    This route demotes the specified user to the regular role in the table.

    Args:
        table_id (int): The ID of the table where the user is being demoted.

    Returns:
        Response: Redirects to the users page for the specified table.
    """
    if request.method == 'POST':
        user_id = request.form['user_id']
        user = db.get_or_404(UserTable, [user_id, table_id])
        user.role = Role.REGULAR
        db.session.commit()

    return redirect(url_for('users.users', table_id=table_id))


@users_bp.route('/tables/<int:table_id>/kick-user', methods=['POST'])
@login_required
def kick_user(table_id: int) -> Response:
    """
    Handles removing a user from the table.

    This route removes the specified user from the table and updates any tasks they are
    working on to 'to do' status. An activity log entry is also saved.

    Args:
        table_id (int): The ID of the table where the user is being removed.

    Returns:
        Response: Redirects to the users page for the specified table.
    """
    if request.method == 'POST':
        user_id = request.form['user_id']
        user = db.get_or_404(UserTable, [user_id, table_id])

        user_tasks = Task.query.filter_by(user_id=user_id,
                                          table_id=table_id,
                                          type=TaskType.IN_PROGRESS)
        for task in user_tasks:
            task.type = TaskType.TO_DO

        save_action(current_user.id, table_id, f'Kicked {user.user.username}')

        db.session.delete(user)
        db.session.commit()

    return redirect(url_for('users.users', table_id=table_id))
