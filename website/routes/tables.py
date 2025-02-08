from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import Table, UserTable, Tag, User, Request, Task, TaskType, Action, Role
from .. import db
from datetime import date


tables_bp = Blueprint('tables', __name__)

@tables_bp.route('/tables', methods=['GET', 'POST'])
@login_required
def tables():
    return render_template('tables.html', user=current_user, tables=current_user.tables)


@tables_bp.route('/tables-enter', methods=['POST'])
@login_required
def enter():
    if request.method == 'POST':
        table_id = request.form['table_id']
        return redirect(url_for('tasks.tasks', table_id=table_id))

    return redirect(url_for('tables.tables'))

# tasks

# tags 


# activity
# users



# settings
