"""
Tables Module

This module handles the management and navigation of tables. It includes routes for
displaying the list of tables a user belongs to and navigating to a specific table.

Routes:
    - `/tables`: Displays the list of tables the current user belongs to.
    - `/tables-enter`: Handles navigation to a specific table based on its ID.

Attributes:
    - tables_bp: The Flask Blueprint for table-related routes.

Functions:
    - tables: Renders the list of tables the current user belongs to.
    - enter: Redirects the user to the tasks page of a specific table.
"""

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.wrappers import Response

tables_bp = Blueprint('tables', __name__)


@tables_bp.route('/tables', methods=['GET', 'POST'])
@login_required
def tables() -> str:
    """
    Displays the list of tables the current user belongs to.

    This route fetches the list of tables associated with the logged-in user and renders
    the 'tables.html' template, passing the user and their tables to the template context.

    Returns:
        str: The rendered 'tables.html' template.
    """
    return render_template('tables.html', user=current_user, tables=current_user.tables)


@tables_bp.route('/tables-enter', methods=['POST'])
@login_required
def enter() -> Response:
    """
    Handles navigation to a specific table.

    This route processes the form submission containing the table ID and redirects the
    user to the tasks page of the specified table.

    Returns:
        Response: Redirects to the tasks page of the specified table or back to the tables page.
    """
    if request.method == 'POST':
        table_id = request.form['table_id']
        return redirect(url_for('tasks.tasks', table_id=table_id))

    return redirect(url_for('tables.tables'))
