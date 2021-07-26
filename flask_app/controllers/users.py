import re
from flask_app import app
from flask import render_template, request, redirect, session, flash
from flask_app.models.user import User
from flask_app.models.recipe import Recipe

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
    recipes = Recipe.get_all_recipes()
    print(recipes)
    return render_template('dashboard.html', recipes = recipes)

# recipes/new route allows user to add recipe, routes from "create" button on /dashboard
@app.route('/recipes/new')
def new_recipe():
    if 'user_id' not in session:
        flash('Must log in to view this page.')
        return redirect('/')
    return render_template('insert_recipes.html')

@app.route('/recipes/create', methods=['POST'])
def create_recipe():
    if Recipe.validate_recipe(request.form):
        data = {
            'recipe_name': request.form['recipe_name'],
            'description': request.form['description'],
            'instructions': request.form['instructions'],
            'date': request.form['date'],
            'under_30': request.form['under_30'],
            'users_id': session['user_id']
        }
        Recipe.create_recipe(data)
        print('recipe valid')
        return redirect('/dashboard')
    print('recipe invalid')
    return redirect('/recipes/new')

# recipes/<recipe_id> route allows user to read recipe card
@app.route('/recipes/<int:recipe_id>')
def read_recipe(recipe_id):
    recipe = Recipe.get_recipe_by_id({'id': recipe_id})
    return render_template('read_recipes.html', recipe = recipe)

# recipes/edit route allows user to edit recipe, routes from "edit" button on dashboard
@app.route('/recipes/<int:recipe_id>/edit/')
def edit_recipe(recipe_id):
    if 'user_id' not in session:
        flash('Must log in to view this page.')
        return redirect('/')
    recipe = Recipe.get_recipe_by_id({'id': recipe_id})
    if session['user_id'] != recipe.users_id:
        return redirect(f'/recipes/{recipe_id}')
    return render_template('update_recipes.html', recipe = recipe)

@app.route('/recipes/<int:recipe_id>/update', methods=['POST'])
def update_recipe(recipe_id):
    if Recipe.validate_recipe(request.form):
        data = {
            'recipe_name': request.form['recipe_name'],
            'description': request.form['description'],
            'instructions': request.form['instructions'],
            'date': request.form['date'],
            'under_30': request.form['under_30'],
            'id': recipe_id
        }
        Recipe.update_recipe(data)
        return redirect(f'/recipes/{recipe_id}')
    return redirect(f'/recipes/{recipe_id}/edit')

@app.route('/recipes/<int:recipe_id>/delete')
def delete_recipe(recipe_id):
    data = {
        'id': recipe_id
    }
    Recipe.delete_recipe_by_id(data)
    return redirect('/dashboard')

# original delete route
# @app.route('/recipes/<int:recipe_id>/delete')
# def delete_recipe(recipe_id):
#     recipe = Recipe.get_recipe_by_id({'id': recipe_id})
#     if session['user_id'] = recipe.users_id:
#         return redirect(f'/recipes/{recipe_id}')
#     return render_template('delete_recipe.html', recipe = recipe)


@app.route('/logout')
def user_logout():
    session.clear()
    return redirect('/')