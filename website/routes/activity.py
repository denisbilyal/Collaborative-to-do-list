from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..models import Table, UserTable
from .. import db

activity_bp = Blueprint('activity', __name__)

@activity_bp.route('/tables/<int:table_id>/activity')
@login_required
def activity(table_id):
    table = db.get_or_404(Table, table_id)  
    user_id = current_user.id
    db.get_or_404(UserTable, [user_id, table_id])

    activities = db.get_or_404(Table, table_id).actions
    return render_template('activity.html', user=current_user, table=table, activities=activities[::-1])

