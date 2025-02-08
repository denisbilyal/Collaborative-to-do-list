from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import Table, UserTable, Tag, User, Request, Task, TaskType, Action, Role
from .. import db
from datetime import date

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/tables/<int:table_id>/settings')
@login_required
def settings(table_id):
    table = db.get_or_404(Table, table_id)
    user_id = current_user.id
    user_table = db.get_or_404(UserTable, [user_id, table_id])
    role = user_table.role

    return render_template('settings.html', user=current_user, table=table, role=role)


@settings_bp.route('/tables/<int:table_id>/edit-table', methods=['POST'])
@login_required
def edit_table(table_id):
    if request.method == 'POST':
        new_table_name = request.form['table_name']

        table = Table.query.filter_by(table_name=new_table_name).first()

        if table is not None:
            flash('Table with this name already exists.', 'error')
            return redirect(url_for('settings.settings', table_id=table_id))


        table = db.get_or_404(Table, table_id)
        table.table_name = new_table_name
        db.session.commit()
        flash('Table successfuly changed.')
    return redirect(url_for('settings.settings', table_id=table_id))



@settings_bp.route('/tables/<int:table_id>/delete-table', methods=['POST'])
@login_required
def delete_table(table_id):
    if request.method == 'POST':
        table = db.get_or_404(Table, table_id)
        db.session.delete(table)
        db.session.commit()
        


    return redirect(url_for('tables.tables'))



@settings_bp.route('/tables/<int:table_id>/leave-table', methods=['POST'])
@login_required
def leave_table(table_id):
    if request.method == 'POST':
        
        user_table_to_delete = db.get_or_404(UserTable, [current_user.id, table_id])

        if user_table_to_delete.role == Role.CREATOR:
            next_creator = UserTable.query.filter_by(table_id=table_id, role=Role.ADMIN).first()

            if next_creator is None:
                next_creator = UserTable.query.filter_by(table_id=table_id, role=Role.REGULAR).first()
            
            if next_creator is None:
                return redirect(url_for('settings.delete_table', table_id=table_id), code=307)
            
            next_creator.role = Role.CREATOR

        
        activity = Action(info=f'Left the table', timestamp=date.today(), table_id=table_id, user_id=current_user.id)
        db.session.add(activity)
        db.session.delete(user_table_to_delete)
        db.session.commit()
        


    return redirect(url_for('tables.tables'))