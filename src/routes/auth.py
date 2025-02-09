"""
Authentication Module

This module handles user authentication, including login, logout, and signup functionalities.
It includes routes for rendering login and signup forms, processing form submissions, and managing
user sessions.

Routes:
    - `/login`: Displays the login page.
    - `/login-enter`: Handles the login form submission.
    - `/sign-up`: Displays the signup page.
    - `/sign-up-create`: Handles the signup form submission.
    - `/logout`: Logs the user out and redirects to the login page.

Attributes:
    - auth: The Flask Blueprint for authentication-related routes.
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.wrappers import Response
from src import db
from ..models import User

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET'])
def login() -> str:
    """
    Displays the login page.

    This route renders the login form. If the user is already logged in, they are
    automatically logged out before accessing this page.

    Returns:
        str: The rendered 'login.html' template.
    """
    logout_user()
    return render_template('login.html', user=current_user)


@auth.route('/login-enter', methods=['POST'])
def login_enter() -> Response:
    """
    Handles the login form submission.

    This route processes the submitted login credentials. If the username and password
    are valid, the user is logged in and redirected to the home page. Otherwise, an
    appropriate error message is displayed.

    Returns:
        Response: Redirects to the home page if login is successful, or back to the
                  login page if it fails.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for('home.home'))
            flash('Wrong password.', 'error')
        else:
            flash('This user does not exist.', 'error')

    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET'])
def sign_up() -> Response:
    """
    Displays the signup page.

    This route renders the signup form. If the user is already logged in, they are
    automatically logged out before accessing this page.

    Returns:
        str: The rendered 'sign_up.html' template.
    """
    logout_user()
    return render_template('sign_up.html', user=current_user)


@auth.route('/sign-up-create', methods=['POST'])
def sign_up_create() -> Response:
    """
    Handles the signup form submission.

    This route processes the submitted signup information. It validates the input,
    checks for username availability, and creates a new user account if all checks pass.
    If successful, the user is redirected to the login page.

    Returns:
        Response: Redirects to the login page if signup is successful, or back to the
                  signup page if validation fails.
    """
    if request.method == 'POST':
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']

        user = db.session.execute(db.select(User).filter_by(username=username)).first()
        if user is not None:
            flash('This username is already taken.', 'error')
        elif len(username) < 3:
            flash('Username must be at least 3 characters long.', 'error')
        elif password1 != password2:
            flash('Passwords do not match.', 'error')
        else:
            new_user = User(
                username=username,
                password=generate_password_hash(password1, method='sha256')
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('auth.login'))

    return redirect(url_for('auth.sign_up'))


@auth.route('/logout')
@login_required
def logout() -> Response:
    """
    Logs the user out.

    This route logs the currently authenticated user out and redirects them
    to the login page.

    Returns:
        Response: Redirects to the login page.
    """
    logout_user()
    return redirect(url_for('auth.login'))
