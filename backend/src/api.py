import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
import sys
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)



'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES

@app.route('/drinks', methods=['GET'])
def get_drinks():
  try: 
    drinks = Drink.query.order_by(Drink.id).all()

    return jsonify({
      "success": True,
      "drinks": [drink.short() for drink in drinks]
    })
  except:
    print(sys.exc_info())
    abort(400)

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
  try: 
    drinks = Drink.query.order_by(Drink.id).all()

    return jsonify({
      "success": True,
      "drinks": [drink.long() for drink in drinks]
    })
  except:
    abort(400)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(jwt):
  body = request.get_json()
  new_title = body.get("title", None)
  new_recipe = body.get("recipe", None)

  try:
    formatted_recipe = json.dumps(new_recipe)
    
    drink = Drink(title=new_title, recipe=formatted_recipe)
    drink.insert()
    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    })
  except:
    print(sys.exc_info())
    abort(422)


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, id):
  try:
    drink = Drink.query.get(id)
    if drink is None:
      abort(404)

    body = request.get_json()
    if "title" in body:
      drink.title = body.get("title", None)

    if "recipe" in body:
      recipe = body.get("recipe", None)
      drink.recipe = json.dumps(recipe)

      drink.update()

    return jsonify({
      "success": True,
      "drinks": [drink.long()]
    })

  except:
    print(sys.exc_info())
    abort(422)

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
  try:
    drink = Drink.query.get(id)
    if drink is None:
      abort(404)
    drink.delete()
    return jsonify({
      "success": True,
      "id": drink.id
    })
  except:
    abort(422)

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
  return jsonify({
    "success": False,
    "error": 404,
    "message": "resource not found"
    }), 404

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401

@app.errorhandler(AuthError)
def process_AuthError(error):
    response = jsonify(error.error)
    response.status_code = error.status_code

    return response

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
