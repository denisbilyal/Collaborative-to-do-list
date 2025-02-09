"""
Home Module

This module handles the home page and table creation functionality.
It includes routes for rendering the home page and creating new tables.

Routes:
    - `/`: Displays the home page.
    - `/create_table`: Handles the creation of a new table.

Attributes:
    - home_bp: The Flask Blueprint for home-related routes.

Functions:
    - home: Renders the home page.
    - create_table: Creates a new table and assigns the current user as the creator.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.wrappers import Response
from src import db
from ..models import Table, UserTable, Role
from .activity import save_action

home_bp = Blueprint('home', __name__)


@home_bp.route('/', methods=['GET'])
@login_required
def home() -> str:
    """
    Displays the home page.

    This route renders the home page template and passes the currently logged-in user
    to the template context.

    Returns:
        str: The rendered 'home.html' template.
    """
    return render_template('home.html', user=current_user)


@home_bp.route('/create_table', methods=['POST'])
@login_required
def create_table() -> Response:
    """
    Handles the creation of a new table.

    This route processes the form submission for creating a new table. If the table name
    is unique, a new table is created, and the current user is assigned as the creator
    with the `CREATOR` role. An activity log entry is also saved.

    Returns:
        Response: Redirects to the home page with a success or error message.
    """
    if request.method == 'POST':
        table_name = request.form['table_name']

        table = Table.query.filter_by(table_name=table_name).first()
        if table is None:
            new_table = Table(table_name=table_name)
            db.session.add(new_table)
            db.session.commit()

            new_user_table = UserTable(
                user_id=current_user.id,
                table_id=new_table.id,
                role=Role.CREATOR
            )
            db.session.add(new_user_table)

            save_action(current_user.id, new_table.id, 'Joined the table')

            db.session.commit()

            flash('Table successfully created.')
        else:
            flash('Table with this name already exists.', 'error')

    return redirect(url_for('home.home'))
