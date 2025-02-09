"""
Requests Module

This module handles user invitations to join tables. It includes routes for displaying
pending invitations, accepting invitations, and declining invitations.

Routes:
    - `/requests`: Displays the pending invitations page.
    - `/requests-accept`: Handles the acceptance of an invitation.
    - `/requests-decline`: Handles the decline of an invitation.

Attributes:
    - requests_bp: The Flask Blueprint for request-related routes.

Functions:
    - requests: Renders the pending invitations page.
    - accept: Accepts a table invitation and adds the user to the table.
    - decline: Declines a table invitation and removes it from the system.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.wrappers import Response
from src import db
from ..models import UserTable, Role, Request
from .activity import save_action

requests_bp = Blueprint('requests', __name__)


@requests_bp.route('/requests', methods=['GET'])
@login_required
def requests() -> str:
    """
    Displays the pending invitations page.

    This route renders the 'requests.html' template, passing the currently logged-in
    user to the template context. The template displays all pending invitations for
    the user.

    Returns:
        str: The rendered 'requests.html' template.
    """
    return render_template('requests.html', user=current_user)


@requests_bp.route('/requests-accept', methods=['POST'])
@login_required
def accept() -> Response:
    """
    Handles the acceptance of a table invitation.

    This route processes the form submission for accepting an invitation. If the
    invitation exists, the user is added to the table with the `REGULAR` role, the
    invitation is removed from the database, and an activity log entry is saved.

    Returns:
        Response: Redirects to the pending invitations page with a success message.
    """
    if request.method == 'POST':
        table_id = request.form['table_id']

        user_table = UserTable(user_id=current_user.id, table_id=table_id, role=Role.REGULAR)
        db.session.add(user_table)

        invite = db.get_or_404(Request, [current_user.id, table_id])
        db.session.delete(invite)

        save_action(current_user.id, table_id, 'Joined the table')

        db.session.commit()

        flash('Invitation successfully accepted.')

    return redirect(url_for('requests.requests'))


@requests_bp.route('/requests-decline', methods=['POST'])
@login_required
def decline() -> Response:
    """
    Handles the decline of a table invitation.

    This route processes the form submission for declining an invitation. If the
    invitation exists, it is removed from the database.

    Returns:
        Response: Redirects to the pending invitations page with a success message.
    """
    if request.method == 'POST':
        table_id = request.form['table_id']

        invite = db.get_or_404(Request, [current_user.id, table_id])
        db.session.delete(invite)

        db.session.commit()

        flash('Invitation successfully declined.', 'error')

    return redirect(url_for('requests.requests'))
