from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from ..models import Table, UserTable, Tag, User, Request
from .. import db

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
        return redirect(url_for('tables.tasks', table_id=table_id))

    return redirect(url_for('tables.tables'))

# tasks
@tables_bp.route('/tables/<int:table_id>')
@login_required
def tasks(table_id):
    table = db.get_or_404(Table, table_id)
    user_id = current_user.id
    db.get_or_404(UserTable, [user_id, table_id])

    return render_template('tasks.html', user=current_user, table=table)

# tags 
@tables_bp.route('/tables/<int:table_id>/tags')
@login_required
def tags(table_id):
    table = db.get_or_404(Table, table_id)
    user_id = current_user.id
    db.get_or_404(UserTable, [user_id, table_id])

    tags = db.get_or_404(Table, table_id).tags

    return render_template('tags.html', user=current_user, table=table, tags=tags)


@tables_bp.route('/tables/<int:table_id>/create-tag', methods=['POST'])
@login_required
def create_tag(table_id):
    if request.method == 'POST':
        tag_name = request.form['tag_name']
        tag = Tag.query.filter_by(name=tag_name, table_id=table_id).first()

        if tag is None:
            tag = Tag(name=tag_name, table_id=table_id)
            db.session.add(tag)
            db.session.commit()
        else:
            pass
            # flash it exists


    return redirect(url_for('tables.tags', table_id=table_id))



@tables_bp.route('/tables/<int:table_id>/update-tag', methods=['POST'])
@login_required
def update_tag(table_id):
    if request.method == 'POST':
        tag_id = request.form['tag_id']
        tag = db.get_or_404(Tag, tag_id)

        new_tag_name = request.form['new_tag_name']
        old_tag = Tag.query.filter_by(name=new_tag_name, table_id=table_id).first()

        if old_tag is None:
            tag.name = new_tag_name
            db.session.commit()
        else:
            pass
            # already exists name


    return redirect(url_for('tables.tags', table_id=table_id))



@tables_bp.route('/tables/<int:table_id>/delete-tag', methods=['POST'])
@login_required
def delete_tag(table_id):
    if request.method == 'POST':
        tag_id = request.form['tag_id']
        tag = db.get_or_404(Tag, tag_id)
        db.session.delete(tag)
        db.session.commit()


    return redirect(url_for('tables.tags', table_id=table_id))


# activity
@tables_bp.route('/tables/<int:table_id>/activity')
@login_required
def activity(table_id):
    table = db.get_or_404(Table, table_id)  
    user_id = current_user.id
    db.get_or_404(UserTable, [user_id, table_id])

    activities = db.get_or_404(Table, table_id).actions
    return render_template('activity.html', user=current_user, table=table, activities=activities)

# users
@tables_bp.route('/tables/<int:table_id>/users')
@login_required
def users(table_id):
    table = db.get_or_404(Table, table_id)  
    user_id = current_user.id
    db.get_or_404(UserTable, [user_id, table_id])

    users = [el.user for el in db.get_or_404(Table, table_id).users]

    return render_template('users.html', user=current_user, table=table, users=users)


@tables_bp.route('/tables/<int:table_id>/invite-user', methods=['POST'])
@login_required
def invite_user(table_id):
    if request.method == 'POST':
        username = request.form['username']
        
        user = User.query.filter_by(username=username).first()

        if user is None:
            print('it doesnt exists')
            return redirect(url_for('tables.users', table_id=table_id))
            # flash it doesnt exists
        
        user_table = UserTable.query.filter_by(user_id=user.id, table_id=table_id).first()

        if user_table is not None:
            print('he is here')
            return redirect(url_for('tables.users', table_id=table_id))
            # user is already in the table
        
        invite = Request.query.filter_by(recipient_id=user.id, table_id=table_id).first()

        if invite:
            print('he already invited')
            return redirect(url_for('tables.users', table_id=table_id))
            # user already is invited to this table

        invite = Request(sender_id=current_user.id, recipient_id=user.id, table_id=table_id)
        db.session.add(invite)
        db.session.commit()

    return redirect(url_for('tables.users', table_id=table_id))
