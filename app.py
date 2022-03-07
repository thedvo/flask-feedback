from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import *
from forms import *
from sqlalchemy.exc import IntegrityError
import os
import re

uri = os.environ.get('DATABASE_URL', 'postgresql:///feedback')
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', 'secret')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)


# ERROR Routes

@app.errorhandler(404)
def page_not_found(e):
    return render_template('status_code/404.html'), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('status_code/405.html'), 405


# USER ROUTES
@app.route('/')
def root():
    """Redirects to register route"""
    return redirect('/register')


@app.route('/register', methods = ['GET', 'POST'])
def register_user():
    """Shows register form and handles its submission"""
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)

        try:
            db.session.commit()

        except IntegrityError:
            form.username.errors.append('Username taken. Please pick another')
            return render_template('user/register.html', form=form)
        
        session['username'] = new_user.username
        flash('Welcome! Successfully Created Your Account!', "success")

        return redirect(f'/users/{new_user.username}')

    return render_template('user/register.html', form=form)


@app.route('/login', methods = ['GET', 'POST'])
def user_login(): 
    """Shows login form and handles its submission"""
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session['username'] = user.username
            flash(f"Welcome Back, {user.username}!", "primary")

            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('user/login.html', form=form)


@app.route('/secret')
def secret():
    """Returns text 'You made it!'"""
    if 'username' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')

    return render_template('user/secret.html')


@app.route('/logout', methods=['POST'])
def logout_user():
    """Logs out user"""

    session.pop('username')
    flash("Successfully Logged Out.", "info")


    return redirect('/')


@app.route('/users/<username>')
def user_page(username):
    """Page displays information on a user"""

    if 'username' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')

    user = User.query.get_or_404(username)
    feedback = Feedback.query.filter(Feedback.username == username)

    return render_template('user/user.html', user=user, feedback=feedback)


@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """Deletes user and all of their feedback"""
    
    if 'username' not in session or session['username'] != username:
        flash("You do not have permission to do this!", "danger")
        return redirect('/home')


    user = User.query.get_or_404(username)
    db.session.delete(user)
    db.session.commit()
    
    session.pop('username')

    flash("User delete successfull.", "success")

    return redirect('/')
    


# FEEDBACK ROUTES

@app.route('/home')
def list_all_feedback():
    """Home page showing all user feedback"""

    feedback = Feedback.query.all()

    return render_template('feedback/list.html', feedback=feedback)


@app.route('/users/<username>/feedback/add', methods=['GET','POST'])
def add_feedback(username):
    """Renders feedback form and handles submit"""
    
    if 'username' not in session or username != session['username'] :
        flash("You do not have permission to do this!", "danger")
        return redirect('/home')

    user = User.query.get_or_404(username)
    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        new_feedback = Feedback(title=title, content=content, username=username)
        db.session.add(new_feedback)
        db.session.commit()

        return redirect(f'/users/{username}')

    return render_template('feedback/add_feedback.html', user=user, form=form)


@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    """Renders update feedback form and handles submit"""

    feedback = Feedback.query.get_or_404(feedback_id)

    if 'username' not in session or session['username'] != feedback.username:
        flash("You do not have permission to do this!", "danger")
        return redirect('/home')

    feedback = Feedback.query.get_or_404(feedback_id)
    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        flash("Feedback successfully updated.", "success")

        return redirect(f"/users/{feedback.username}")
    
    else:
        return render_template('feedback/update_feedback.html', feedback=feedback, form=form)


@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    """Deletes feedback"""

    if 'username' not in session:
        flash("You do not have permission to do this!", "danger")
        return redirect('/login')

    feedback = Feedback.query.get_or_404(feedback_id)
    user = session['username']

    if feedback.username == user:
        db.session.delete(feedback)
        db.session.commit()
        
        flash("Message has been deleted", "success")

        return redirect(f'/users/{user}')
    
    return redirect(f'/users/{user}')
