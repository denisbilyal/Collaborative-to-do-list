from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from ..models import Table, UserTable, Role
from .. import db

home_bp = Blueprint('home', __name__)

@home_bp.route('/', methods=['GET'])
@login_required
def home():
    return render_template('home.html', user=current_user)


@home_bp.route('/create_table', methods=['POST'])
@login_required
def create_table():
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
        else:
            pass
            # flash existing table name

    return redirect(url_for('home.home'))
