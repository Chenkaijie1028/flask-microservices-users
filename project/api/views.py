from flask import Blueprint, jsonify, request, render_template
from sqlalchemy import exc
from project import db
from project.api.models import User

users_blueprint = Blueprint('users', __name__)

@users_blueprint.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })

@users_blueprint.route('/users', methods=['GET'])
def get_users():
    response_object = {
        'status': 'success',
        'data': {
            "users": []
        }
    }
    code = 200
    try:
        users = User.query.all()
        datas = []
        for user in users:
            data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at
            }
            datas.append(data)
            code = 200
        response_object = {
            'status': 'success',
            'data': {
                "users": datas
            }
        }
    except ValueError:
        response_object = {
            'status': 'fail',
        }
        code = 400
    finally:
        return jsonify(response_object), code

@users_blueprint.route('/users', methods=['POST'])
def add_user():
    post_data = request.get_json()
    if not post_data:
        response_data = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return jsonify(response_data), 400
    email = post_data.get('email')
    username = post_data.get('username')
    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            db.session.add(User(username=username, email=email))
            db.session.commit()
            response_data = {
                'status': 'success',
                'message': '%s was added!' % email
            }
            return jsonify(response_data), 201
        response_data = {
            'status': 'fail',
            'message': 'Sorry. That email already exists.'
        }
        return jsonify(response_data), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        response_data = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return jsonify(response_data), 400

@users_blueprint.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    response_object = {
        'status': 'fail',
        'message': 'User does not exist'
    }
    code = 404
    try:
        user = User.query.filter_by(id=int(user_id)).first()
        if user:
            response_object = {
                'status': 'success',
                'data': {
                    'username': user.username,
                    'email': user.email,
                    'created_at': user.created_at
                }
            }
            code = 200
    except ValueError:
        response_object = {
            'status': 'fail',
            'message': 'Param id error'
        }
        code = 400
    finally:
        return jsonify(response_object), code