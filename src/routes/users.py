from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import Table, UserTable, Tag, User, Request, Task, TaskType, Action, Role
from .. import db
from datetime import date

users_bp = Blueprint('users', __name__)

@users_bp.route('/tables/<int:table_id>/users')
@login_required
def users(table_id):
    table = db.get_or_404(Table, table_id)  
    user_id = current_user.id
    db.get_or_404(UserTable, [user_id, table_id])

    users_in_table = UserTable.query.filter_by(table_id=table_id)
    user_table = db.get_or_404(UserTable, [user_id, table_id])
    role = user_table.role
    return render_template('users.html', user=current_user, table=table, users_in_table=users_in_table, role=role)


@users_bp.route('/tables/<int:table_id>/invite-user', methods=['POST'])
@login_required
def invite_user(table_id):
    if request.method == 'POST':
        username = request.form['username']
        
        user = User.query.filter_by(username=username).first()

        if user is None:
            flash('This user does not exists.', 'error')
            return redirect(url_for('users.users', table_id=table_id))
        
        user_table = UserTable.query.filter_by(user_id=user.id, table_id=table_id).first()

        if user_table is not None:
            flash('This user is already in the table.', 'error')
            return redirect(url_for('users.users', table_id=table_id))
        
        invite = Request.query.filter_by(recipient_id=user.id, table_id=table_id).first()

        if invite:
            flash('This user is already invited.', 'error')
            return redirect(url_for('users.users', table_id=table_id))
            # user already is invited to this table

        invite = Request(sender_id=current_user.id, recipient_id=user.id, table_id=table_id)
        db.session.add(invite)
        db.session.commit()
        flash('User successfuly invited.',)

    return redirect(url_for('users.users', table_id=table_id))


@users_bp.route('/tables/<int:table_id>/promote-user', methods=['POST'])
@login_required
def promote_user(table_id):
    if request.method == 'POST':
        user_id = request.form['user_id']
        user = db.get_or_404(UserTable, [user_id, table_id])
        user.role = Role.ADMIN
        db.session.commit()

    return redirect(url_for('users.users', table_id=table_id))


@users_bp.route('/tables/<int:table_id>/demote-user', methods=['POST'])
@login_required
def demote_user(table_id):
    if request.method == 'POST':
        user_id = request.form['user_id']
        user = db.get_or_404(UserTable, [user_id, table_id])
        user.role = Role.REGULAR
        db.session.commit()

    return redirect(url_for('users.users', table_id=table_id))


@users_bp.route('/tables/<int:table_id>/kick-user', methods=['POST'])
@login_required
def kick_user(table_id):
    if request.method == 'POST':
        user_id = request.form['user_id']
        user = db.get_or_404(UserTable, [user_id, table_id])

        user_tasks = Task.query.filter_by(user_id=user_id, table_id=table_id, type=TaskType.IN_PROGRESS)

        for task in user_tasks:
            task.type = TaskType.TO_DO

        activity = Action(info=f'Was kicked by {current_user.username}', timestamp=date.today(), table_id=table_id, user_id=current_user.id)
        db.session.add(activity)
        db.session.delete(user)
        db.session.commit()

    return redirect(url_for('users.users', table_id=table_id))
