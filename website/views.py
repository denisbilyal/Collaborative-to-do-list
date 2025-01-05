from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import login_required, current_user
from .models import Table, UserTable, Role
from . import db
from sqlalchemy.sql.expression import select

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        table_name = request.form['table_name']
        table = Table.query.filter_by(table_name=table_name).first()
        
        if table is None:
            new_table = Table(table_name=table_name)
            db.session.add(new_table)
            db.session.commit()

            new_user_table = UserTable(user_id=current_user.id, table_id=new_table.id, role=Role.CREATOR)
            db.session.add(new_user_table)
            db.session.commit()
            print('created')
        else:
            print('didnt')
            pass
        # flash existing table name

    return render_template('home.html', user=current_user)

@views.route('/tables', methods=['GET', 'POST'])
@login_required
def tables():
    if request.method == 'POST':
        table_id = request.form['table_id']
        return redirect(url_for('views.in_table', table_id=table_id))
    return render_template('tables.html', user=current_user, tables=current_user.tables)

@views.route('/requests', methods=['GET', 'POST'])
@login_required
def requests():
    return render_template('requests.html', user=current_user)

@views.route('/tables/<int:table_id>')
@login_required
def in_table(table_id):
    table = db.get_or_404(Table, table_id)  
    user_id = current_user.id
    db.get_or_404(UserTable, [user_id, table_id])

    return render_template('in_table.html', user=current_user, table=table)