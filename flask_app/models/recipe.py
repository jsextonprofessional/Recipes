from flask import flash
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models.user import User

class Recipe():
    def __init__(self, data):
        self.id = data['id']
        self.recipe_name = data['recipe_name']
        self.description = data['description']
        self.instructions = data['instructions']
        self.date = data['date']
        self.under_30 = data['under_30']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.users_id = data['users_id']
        self.user = []

    @classmethod
    def create_recipe(cls, data):
        query = 'INSERT INTO recipes (recipe_name, description, instructions, date, under_30, users_id) VALUES (%(recipe_name)s, %(description)s, %(instructions)s, %(date)s, %(under_30)s, %(users_id)s);'
        result = connectToMySQL('recipes_schema').query_db(query, data)
        return result

    @classmethod
    def get_all_recipes(cls):
        query = 'SELECT * FROM recipes JOIN users ON users.id = recipes.users_id;'
        results = connectToMySQL('recipes_schema').query_db(query)
        recipes = []
        for item in results:
            recipe = cls(item)
            user_data = {
                'id': item['id'],
                'first_name': item['first_name'],
                'last_name': item['last_name'],
                'email': item['email'],
                'password': item['password'],
                'created_at': item['created_at'],
                'updated_at': item['updated_at']
            }
            recipe.user = User(user_data)
            recipes.append(recipe)

        return recipes

    @classmethod
    def get_recipe_by_id(cls, data):
        query = 'SELECT * FROM recipes WHERE id = %(id)s;'
        results = connectToMySQL('recipes_schema').query_db(query, data)
        recipe = Recipe(results[0])
        print(recipe)
        return recipe

    @classmethod
    def update_recipe(cls, data):
        query = 'UPDATE recipes SET recipe_name = %(recipe_name)s, description = %(description)s, instructions = %(instructions)s, date = %(date)s, under_30 = %(under_30)s WHERE id = %(id)s;'
        connectToMySQL('recipes_schema').query_db(query, data)

    @classmethod
    def delete_recipe(cls, data):
        query = 'DELETE FROM recipes WHERE id = %(id)s;'
        connectToMySQL('recipes_schema').query_db(query, data)

    @staticmethod
    def validate_recipe(data):
        is_valid = True
        if len(data['recipe_name']) < 1 or len(data['recipe_name']) > 45:
            flash('Recipe name must be 1-45 character.')
            is_valid = False
        if len(data['description']) < 1 or len(data['description']) > 255:
            flash('Recipe description must be 1-255 characters.')
            is_valid = False
        if len(data['instructions']) < 1 or len(data['instructions']) > 255:
            flash('Recipe instructions must be 1-255 characters.')
            is_valid = False
        if len(data['date']) == 0:
            flash('Must include date.')
            is_valid = False
        
        return is_valid