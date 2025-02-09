"""
Tags Module

This module handles tag-related functionality for tables, including displaying tags,
creating new tags, updating existing tags, and deleting tags.

Routes:
    - `/tables/<int:table_id>/tags`: Displays the list of tags for a specific table.
    - `/tables/<int:table_id>/create-tag`: Handles the creation of a new tag.
    - `/tables/<int:table_id>/update-tag`: Handles the updating of an existing tag.
    - `/tables/<int:table_id>/delete-tag`: Handles the deletion of a tag.

Attributes:
    - tags_bp: The Flask Blueprint for tag-related routes.

Functions:
    - tags: Renders the list of tags for a specific table.
    - create_tag: Creates a new tag for the specified table.
    - update_tag: Updates an existing tag's name.
    - delete_tag: Deletes a tag if no tasks are associated with it.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.wrappers import Response
from src import db
from ..models import Table, UserTable, Tag, Task

tags_bp = Blueprint('tags', __name__)


@tags_bp.route('/tables/<int:table_id>/tags')
@login_required
def tags(table_id: int) -> str:
    """
    Displays the list of tags for a specific table.

    This route fetches the table and its associated tags, ensuring the user has access
    to the table before rendering the 'tags.html' template.

    Args:
        table_id (int): The ID of the table whose tags are being viewed.

    Returns:
        str: The rendered 'tags.html' template.
    """
    table = db.get_or_404(Table, table_id)
    user_id = current_user.id
    db.get_or_404(UserTable, [user_id, table_id])
    tags_in_table = db.get_or_404(Table, table_id).tags
    return render_template('tags.html', user=current_user, table=table, tags=tags_in_table)


@tags_bp.route('/tables/<int:table_id>/create-tag', methods=['POST'])
@login_required
def create_tag(table_id: int) -> Response:
    """
    Handles the creation of a new tag for a specific table.

    This route processes the form submission for creating a new tag. If the tag name is
    unique within the table, the tag is created. Otherwise, no action is taken.

    Args:
        table_id (int): The ID of the table where the tag will be created.

    Returns:
        Response: Redirects to the tags page for the specified table.
    """
    if request.method == 'POST':
        tag_name = request.form['tag_name']
        tag = Tag.query.filter_by(name=tag_name, table_id=table_id).first()

        if tag is None:
            tag = Tag(name=tag_name, table_id=table_id)
            db.session.add(tag)
            db.session.commit()
        else:
            flash('This tag already exists in this table.', 'error')

    return redirect(url_for('tags.tags', table_id=table_id))


@tags_bp.route('/tables/<int:table_id>/update-tag', methods=['POST'])
@login_required
def update_tag(table_id: int) -> Response:
    """
    Handles the updating of an existing tag's name.

    This route processes the form submission for updating a tag's name. If the new name
    is unique within the table, the tag is updated. Otherwise, an error message is displayed.

    Args:
        table_id (int): The ID of the table containing the tag.

    Returns:
        Response: Redirects to the tags page for the specified table.
    """
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
def delete_tag(table_id: int) -> Response:
    """
    Handles the deletion of a tag.

    This route processes the form submission for deleting a tag. If the tag is associated
    with any tasks, deletion is prevented, and an error message is displayed. Otherwise,
    the tag is deleted.

    Args:
        table_id (int): The ID of the table containing the tag.

    Returns:
        Response: Redirects to the tags page for the specified table.
    """
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
