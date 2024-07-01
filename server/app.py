from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, User, Recipe

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    image_url = data.get('image_url')
    bio = data.get('bio')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 422

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 422

    user = User(username=username, image_url=image_url, bio=bio)
    user.password_hash = password

    db.session.add(user)
    db.session.commit()

    session['user_id'] = user.id

    return jsonify({
        'id': user.id,
        'username': user.username,
        'image_url': user.image_url,
        'bio': user.bio
    }), 201

@app.route('/check_session', methods=['GET'])
def check_session():
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    user = User.query.get(user_id)

    return jsonify({
        'id': user.id,
        'username': user.username,
        'image_url': user.image_url,
        'bio': user.bio
    }), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401

    session['user_id'] = user.id

    return jsonify({
        'id': user.id,
        'username': user.username,
        'image_url': user.image_url,
        'bio': user.bio
    }), 200

@app.route('/logout', methods=['DELETE'])
def logout():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    session.pop('user_id', None)

    return '', 401

@app.route('/recipes', methods=['GET', 'POST'])
def recipes():
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    if request.method == 'GET':
        recipes = Recipe.query.all()
        return jsonify([
            {
                'id': recipe.id,
                'title': recipe.title,
                'instructions': recipe.instructions,
                'minutes_to_complete': recipe.minutes_to_complete,
                'user': {
                    'id': recipe.user.id,
                    'username': recipe.user.username,
                    'image_url': recipe.user.image_url,
                    'bio': recipe.user.bio
                }
            } for recipe in recipes
        ]), 200

    if request.method == 'POST':
        data = request.get_json()
        title = data.get('title')
        instructions = data.get('instructions')
        minutes_to_complete = data.get('minutes_to_complete')

        if not title or not instructions or len(instructions) < 50:
            return jsonify({'error': 'Invalid recipe data'}), 422

        recipe = Recipe(
            title=title,
            instructions=instructions,
            minutes_to_complete=minutes_to_complete,
            user_id=user_id
        )

        db.session.add(recipe)
        db.session.commit()

        return jsonify({
            'id': recipe.id,
            'title': recipe.title,
            'instructions': recipe.instructions,
            'minutes_to_complete': recipe.minutes_to_complete,
            'user': {
                'id': recipe.user.id,
                'username': recipe.user.username,
                'image_url': recipe.user.image_url,
                'bio': recipe.user.bio
            }
        }), 201

if __name__ == '__main__':
    app.run(debug=True)
