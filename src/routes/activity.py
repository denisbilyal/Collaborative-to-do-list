"""
Module for handling activity-related routes.

This module defines a Blueprint for managing the activity logs of a specific table.
It includes functionality to save actions to the database and display the activity
logs for a given table.

Functions:
    - save_action: Saves an action to the database.
    - activity: Displays the activity logs for a specific table.

Attributes:
    - activity_bp: The Flask Blueprint for activity-related routes.
"""

from datetime import date
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from src import db
from ..models import Table, UserTable, Action


def save_action(user_id: int, table_id: int, info: str) -> None:
    """
    Saves an action to the database.

    Args:
        user_id (int): The ID of the user performing the action.
        table_id (int): The ID of the table associated with the action.
        info (str): A description of the action.

    Returns:
        None
    """
    new_activity = Action(
        info=info,
        timestamp=date.today(),
        table_id=table_id,
        user_id=user_id
    )
    db.session.add(new_activity)
    db.session.commit()


# Create a Blueprint for activity-related routes
activity_bp = Blueprint('activity', __name__)


@activity_bp.route('/tables/<int:table_id>/activity')
@login_required
def activity(table_id: int) -> str:
    """
    Displays the activity logs for a specific table.

    Args:
        table_id (int): The ID of the table whose activity logs are to be displayed.

    Returns:
        str: The rendered 'activity.html' template with the following context:
            - user: The currently logged-in user.
            - table: The table object corresponding to the given table ID.
            - activities: The list of activity logs for the table, in reverse chronological order.
    """
    table = db.get_or_404(Table, table_id)

    user_id = current_user.id

    db.get_or_404(UserTable, [user_id, table_id])

    activities = db.get_or_404(Table, table_id).actions

    return render_template(
        'activity.html',
        user=current_user,
        table=table,
        activities=activities[::-1]
    )
