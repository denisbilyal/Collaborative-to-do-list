from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import Table, UserTable, Tag, Priority, Task, TaskType, Action
from .. import db
from datetime import date
from flask_socketio import join_room
from .. import socketio

@socketio.on('join_room')
def on_join_room(room_name):
    join_room(room_name)
    print(f"Client joined room: {room_name}")

def emit_changes(table_id):
    tasks_to_do = [task_to_dict(task) for task in list(Task.query.filter_by(table_id=table_id, type=TaskType.TO_DO))]
    tasks_progress = [task_to_dict(task) for task in list(Task.query.filter_by(table_id=table_id, type=TaskType.IN_PROGRESS))]
    tasks_finished = [task_to_dict(task) for task in list(Task.query.filter_by(table_id=table_id, type=TaskType.COMPLETED))]

    socketio.emit('update_tasks', {
    "tasks_to_do": tasks_to_do,
    "tasks_progress": tasks_progress,
    "tasks_finished": tasks_finished
    }, room=f'table_{table_id}')


def task_to_dict(task):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "tag": {"name": task.tag.name} if task.tag else None,
        "priority": {"name": task.priority.name} if task.priority else None,
        "user": {"username": task.user.username} if task.user else None,
        "due_date": f"{task.due_date[8:10]}/{task.due_date[5:7]}/{task.due_date[0:4]}" if task.due_date else None,
        "date": f"{task.date[8:10]}/{task.date[5:7]}/{task.date[0:4]}" if task.date else None
    }

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/tables/<int:table_id>')
@login_required
def tasks(table_id):
    table = db.get_or_404(Table, table_id)
    user_id = current_user.id
    db.get_or_404(UserTable, [user_id, table_id])
    tags = Tag.query.filter_by(table_id=table_id)
    
    tasks_to_do = [task_to_dict(task) for task in list(Task.query.filter_by(table_id=table_id, type=TaskType.TO_DO))]
    tasks_progress = [task_to_dict(task) for task in list(Task.query.filter_by(table_id=table_id, type=TaskType.IN_PROGRESS))]
    tasks_finished = [task_to_dict(task) for task in list(Task.query.filter_by(table_id=table_id, type=TaskType.COMPLETED))]

    max_rows = max([len(tasks_to_do), len(tasks_progress), len(tasks_finished)])
    
    return render_template('tasks.html', 
                           user=current_user, 
                           table=table, 
                           priorities=Priority, 
                           tags=tags, 
                           tasks_to_do=tasks_to_do, 
                           tasks_progress=tasks_progress,
                           tasks_finished=tasks_finished,
                           max_rows=max_rows,
                           user_id=current_user.id)


@tasks_bp.route('/tables/<int:table_id>/create-task', methods=['POST'])
@login_required
def create_task(table_id):
    if request.method == 'POST':
        title = request.form['task_name']
        description = request.form['task_description']
        tag_id = request.form.get('tag_id')
        priority = request.form['priority']
        due_date = request.form['due_date']
        
        if tag_id is None:
            flash('Cannot create task without a tag.', 'error')
            return redirect(url_for('tasks.tasks', table_id=table_id))
        elif due_date == '':
            flash('Invalid due date.', 'error')
            return redirect(url_for('tasks.tasks', table_id=table_id))
        
        print(type(due_date))

        task = Task(title=title, 
                    description=description, 
                    priority=priority, 
                    date=date.today().strftime('%Y-%m-%d'), 
                    due_date=due_date, 
                    type=TaskType.TO_DO, 
                    tag_id=tag_id, 
                    user_id=current_user.id, 
                    table_id=table_id)
        
        db.session.add(task)

        activity = Action(info=f'Created a task: {task.title}', timestamp=date.today(), table_id=table_id, user_id=current_user.id)
        db.session.add(activity)

        db.session.commit()

        emit_changes(table_id)
    
    return redirect(url_for('tasks.tasks', table_id=table_id))

@tasks_bp.route('/tables/<int:table_id>/start-task', methods=['POST'])
@login_required
def start_task(table_id):
    if request.method == 'POST':
        task_id = request.form['task_id']
        task = db.get_or_404(Task, task_id)

        task.type = TaskType.IN_PROGRESS
        task.user_id = current_user.id
        
        db.session.commit()

        emit_changes(table_id)


    return redirect(url_for('tasks.tasks', table_id=table_id))

@tasks_bp.route('/tables/<int:table_id>/delete-task', methods=['POST'])
@login_required
def delete_task(table_id):
    if request.method == 'POST':
        task_id = request.form['task_id']
        task = db.get_or_404(Task, task_id)
        db.session.delete(task)

        activity = Action(info=f'Deleted a task: {task.title}', timestamp=date.today(), table_id=table_id, user_id=current_user.id)
        db.session.add(activity)
        
        db.session.commit()

        emit_changes(table_id)
        
    return redirect(url_for('tasks.tasks', table_id=table_id))

@tasks_bp.route('/tables/<int:table_id>/reject-task', methods=['POST'])
@login_required
def reject_task(table_id):
    if request.method == 'POST':
        task_id = request.form['task_id']
        task = db.get_or_404(Task, task_id)

        task.type = TaskType.TO_DO

        db.session.commit()

        emit_changes(table_id)

    return redirect(url_for('tasks.tasks', table_id=table_id))



@tasks_bp.route('/tables/<int:table_id>/finish-task', methods=['POST'])
@login_required
def finish_task(table_id):
    if request.method == 'POST':
        task_id = request.form['task_id']
        task = db.get_or_404(Task, task_id)

        task.type = TaskType.COMPLETED
        task.date = date.today().strftime('%Y-%m-%d')

        db.session.commit()

        emit_changes(table_id)
    return redirect(url_for('tables.tasks', table_id=table_id))

@tasks_bp.route('/tables/<int:table_id>/undo-task', methods=['POST'])
@login_required
def undo_task(table_id):
    if request.method == 'POST':
        task_id = request.form['task_id']
        task = db.get_or_404(Task, task_id)

        task.type = TaskType.IN_PROGRESS

        db.session.commit()

        emit_changes(table_id)

    return redirect(url_for('tasks.tasks', table_id=table_id))


@tasks_bp.route('/tables/<int:table_id>/clear-task', methods=['POST'])
@login_required
def clear_task(table_id):
    if request.method == 'POST':
        task_id = request.form['task_id']
        task = db.get_or_404(Task, task_id)
        db.session.delete(task)
        db.session.commit()

        emit_changes(table_id)

    return redirect(url_for('tasks.tasks', table_id=table_id))
