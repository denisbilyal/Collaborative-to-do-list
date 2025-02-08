from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import Table, UserTable, Role, Request, Action
from .. import db
from datetime import date 

requests_bp = Blueprint('requests', __name__)

@requests_bp.route('/requests', methods=['GET'])
@login_required
def requests():
    return render_template('requests.html', user=current_user)


@requests_bp.route('/requests-accept', methods=['POST'])
@login_required
def accept():

    if request.method == 'POST':
        table_id = request.form['table_id']
        user_table = UserTable(user_id=current_user.id, table_id=table_id, role=Role.REGULAR)
        db.session.add(user_table)

        invite = db.get_or_404(Request, [current_user.id, table_id])
        db.session.delete(invite)

        activity = Action(info=f'Joined the table', timestamp=date.today(), table_id=table_id, user_id=current_user.id)
        db.session.add(activity)
        
        db.session.commit()
        flash('Invitation successfully accepted.')


    return redirect(url_for('requests.requests'))



@requests_bp.route('/requests-decline', methods=['POST'])
@login_required
def decline():

    if request.method == 'POST':
        table_id = request.form['table_id']

        invite = db.get_or_404(Request, [current_user.id, table_id])
        db.session.delete(invite)

        db.session.commit()
        flash('Invitation successfully declined.', 'error')

    return redirect(url_for('requests.requests'))