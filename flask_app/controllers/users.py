import re
from flask_app import app
from flask import render_template, request, redirect, session, flash
from flask_app.models.user import User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

# index page displays login or register
@app.route('/')
def index():
    return render_template('index.html')

# users/register route
@app.route('/users/register', methods = ['POST'])
def user_registration():
    if User.registration_validation(request.form):
        data = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email'],
            'password': bcrypt.generate_password_hash(request.form['password'])
        }
        user = User.insert_user(data)
        session['user_id'] = user
        session['first_name'] = request.form['first_name']
        return redirect('/dashboard')
    return redirect('/')

# users/login
@app.route('/users/login', methods=['POST'])
def user_login():
    users = User.select_users_by_email(request.form)
    if len(users) != 1:
        flash('Account associated with that email address does not exist.')
        return redirect('/')
    user = users[0]
    if not bcrypt.check_password_hash(user.password, request.form['password']):
        flash('Incorrect password.')
        return redirect('/')
    session['user_id'] = user.id
    session['first_name'] = user.first_name
    return redirect('/dashboard')

# dashboard is basically homepage after login
@app.route('/dashboard')
def successful_login_page():
    if 'user_id' not in session:
        flash('Must log in to view this page.')
        return redirect('/')
    return render_template('dashboard.html')

# recipes/new route allows user to add recipe, routes from "create" button on /dashboard
@app.route('/recipes/new')
def insert_new_recipe():
    if 'user_id' not in session:
        flash('Must log in to view this page.')
        return redirect('/')
    return render_template('recipes_insert.html')

# recipes/new route allows user to edit recipe, routes from "edit" button on dashboard
@app.route('/recipes/edit/<recipe_id>')
def update_recipe():
    if 'user_id' not in session:
        flash('Must log in to view this page.')
        return redirect('/')
    return render_template('recipes_edit.html')

# recipes/<recipe_id> route allows user to read recipe card
# I WILL NEED TO REWRITE THIS ROUTE AFTER TESTING. CURRENTLY HARDCODING URL FOR TESTING.
@app.route('/recipes/show')
def read_recipe():
    return render_template('recipes_read.html')

# logout route clears session and redirects to index
@app.route('/logout')
def user_logout():
    session.clear()
    return redirect('/')