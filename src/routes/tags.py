from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import Table, UserTable, Tag, User, Request, Task, TaskType, Action, Role
from .. import db
from datetime import date

tags_bp = Blueprint('tags', __name__)

@tags_bp.route('/tables/<int:table_id>/tags')
@login_required
def tags(table_id):
    table = db.get_or_404(Table, table_id)
    user_id = current_user.id
    db.get_or_404(UserTable, [user_id, table_id])

    tags = db.get_or_404(Table, table_id).tags

    return render_template('tags.html', user=current_user, table=table, tags=tags)


@tags_bp.route('/tables/<int:table_id>/create-tag', methods=['POST'])
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


    return redirect(url_for('tags.tags', table_id=table_id))



@tags_bp.route('/tables/<int:table_id>/update-tag', methods=['POST'])
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
            flash('This tag already exists in this table.', 'error')


    return redirect(url_for('tags.tags', table_id=table_id))



@tags_bp.route('/tables/<int:table_id>/delete-tag', methods=['POST'])
@login_required
def delete_tag(table_id):
    if request.method == 'POST':
        tag_id = request.form['tag_id']
        task = Task.query.filter_by(tag_id=tag_id).first()

        if task is not None:
           flash('There are tasks with this tag, cannot delete.', 'error')
           return redirect(url_for('tags.tags', table_id=table_id)) 

        tag = db.get_or_404(Tag, tag_id)
        db.session.delete(tag)
        db.session.commit()


    return redirect(url_for('tags.tags', table_id=table_id))
