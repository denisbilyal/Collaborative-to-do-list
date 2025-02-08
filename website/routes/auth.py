from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, login_user, logout_user, current_user
from ..models import User
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET'])
def login():
    logout_user()
    return render_template('login.html', user=current_user)

@auth.route('/login-enter', methods=['POST'])
def login_enter():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for('home.home'))
            else:
                flash('Wrong password.', 'error')
                
        else:
            flash('This user does not exists.', 'error')

    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET'])
def sign_up():
    logout_user()
    return render_template('sign_up.html', user=current_user)

@auth.route('/sign-up-create', methods=['POST'])
def sign_up_create():
    if request.method == 'POST':
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = db.session.execute(db.select(User).filter_by(username=username)).first()
        if user is not None:
            flash('This username is already taken.', 'error')
        elif len(username) < 3:
            flash('Username must be at least 3 symbols long.', 'error')
        elif password1 != password2:
            flash('Passwords do not match.', 'error')
        else:
            new_user = User(username=username, password=generate_password_hash(password1))
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('auth.login'))

            
    return redirect(url_for('auth.sign_up'))



@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))