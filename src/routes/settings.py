"""
Settings Module

This module handles table settings, including editing, deleting, and leaving tables.
It includes routes for displaying the settings page, editing table names, deleting tables,
and leaving tables.

Routes:
    - `/tables/<int:table_id>/settings`: Displays the settings page for a specific table.
    - `/tables/<int:table_id>/edit-table`: Handles the renaming of a table.
    - `/tables/<int:table_id>/delete-table`: Handles the deletion of a table.
    - `/tables/<int:table_id>/leave-table`: Handles the current user leaving a table.

Attributes:
    - settings_bp: The Flask Blueprint for settings-related routes.

Functions:
    - settings: Renders the settings page for a specific table.
    - edit_table: Renames a table if the new name is unique.
    - delete_table: Deletes a table and removes all associated data.
    - leave_table: Allows the current user to leave a table, transferring ownership if necessary.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.wrappers import Response
from src import db
from ..models import Table, UserTable, Role
from .activity import save_action

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/tables/<int:table_id>/settings')
@login_required
def settings(table_id: int) -> str:
    """
    Displays the settings page for a specific table.

    This route fetches the table and the user's role in the table and renders the
    'settings.html' template with this information.

    Args:
        table_id (int): The ID of the table whose settings are being viewed.

    Returns:
        str: The rendered 'settings.html' template.
    """
    table = db.get_or_404(Table, table_id)
    user_id = current_user.id
    user_table = db.get_or_404(UserTable, [user_id, table_id])
    role = user_table.role
    return render_template('settings.html', user=current_user, table=table, role=role)


@settings_bp.route('/tables/<int:table_id>/edit-table', methods=['POST'])
@login_required
def edit_table(table_id: int) -> Response:
    """
    Handles the renaming of a table.

    This route processes the form submission for renaming a table. If the new name is
    unique, the table name is updated. Otherwise, an error message is displayed.

    Args:
        table_id (int): The ID of the table being renamed.

    Returns:
        Response: Redirects to the settings page with a success or error message.
    """
    if request.method == 'POST':
        new_table_name = request.form['table_name']
        table = Table.query.filter_by(table_name=new_table_name).first()

        if table is not None:
            flash('Table with this name already exists.', 'error')
            return redirect(url_for('settings.settings', table_id=table_id))

        table = db.get_or_404(Table, table_id)
        table.table_name = new_table_name
        db.session.commit()
        flash('Table successfully changed.')

    return redirect(url_for('settings.settings', table_id=table_id))


@settings_bp.route('/tables/<int:table_id>/delete-table', methods=['POST'])
@login_required
def delete_table(table_id: int) -> Response:
    """
    Handles the deletion of a table.

    This route deletes the specified table and all associated data.

    Args:
        table_id (int): The ID of the table being deleted.

    Returns:
        Response: Redirects to the tables overview page.
    """
    if request.method == 'POST':
        table = db.get_or_404(Table, table_id)
        db.session.delete(table)
        db.session.commit()

    return redirect(url_for('tables.tables'))


@settings_bp.route('/tables/<int:table_id>/leave-table', methods=['POST'])
@login_required
def leave_table(table_id: int) -> Response:
    """
    Handles the current user leaving a table.

    This route allows the current user to leave a table. If the user is the creator,
    ownership is transferred to another user (if available). If no other users exist,
    the table is deleted.

    Args:
        table_id (int): The ID of the table the user is leaving.

    Returns:
        Response: Redirects to the tables overview page.
    """
    if request.method == 'POST':
        user_table_to_delete = db.get_or_404(UserTable, [current_user.id, table_id])

        if user_table_to_delete.role == Role.CREATOR:
            next_creator = UserTable.query.filter_by(table_id=table_id,
                                                     role=Role.ADMIN).first()
            if next_creator is None:
                next_creator = UserTable.query.filter_by(table_id=table_id,
                                                         role=Role.REGULAR).first()
            if next_creator is None:
                return redirect(url_for('settings.delete_table', table_id=table_id), code=307)

            next_creator.role = Role.CREATOR

        save_action(current_user.id, table_id, 'Left the table')
        db.session.delete(user_table_to_delete)
        db.session.commit()

    return redirect(url_for('tables.tables'))
