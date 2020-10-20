from flask import Flask, request, jsonify
from py_expression_eval import Parser
import logging

from db import postgres as pg
from settings import * 



app = Flask(__name__)

# TODO: to make a good working Flask logging

db = pg.Postgres(dbname=DB_NAME, user=DB_USER,
                 password=DB_PASSWORD,
                 host=DB_HOST,
                 port=DB_PORT)


def jsonify_msg(msg: str):
    return jsonify({"msg": msg})


def signal_handler(signum, frame):
    raise TimeoutError("Calculation takes to long!")


@app.route("/api/expression", methods=['POST'])
def post_expression():
    try:
        raw_json = request.get_json()
        expression = raw_json['expression']
        variables = raw_json['variables']
    except TypeError:
        return jsonify_msg('No JSON found'), 400
    except KeyError:
        return jsonify_msg('JSON has wrong structure'), 400

    try:
        parser = Parser()
        # mathematical expression validation (yes, we expect hackers in our network)
        parsed_expression = parser.parse(expression)

    # "py_expression_eval" uses Exception class for all exceptions except devision by zero and overflow :(
    except Exception:
        return jsonify_msg('Error when parsing expression'), 400

    # variables matching validation
    variables_set = set(parsed_expression.variables())
    if variables_set != set(variables):
        return jsonify_msg('JSON["variables"] does not match with variables in expression'), 400

    try:
        expression_id = db.put_task(expression, variables)
    except Exception as e:
        logger.warning(e)
        return jsonify_msg("Internal server error occured"), 500

    return jsonify(expression_id[0]), 200


@app.route("/api/result/<expression_id>", methods=['GET'])
def get_expression_result(expression_id):
    try:
        expression_id = int(expression_id)
    except ValueError as e:
        logger.warning(e)
        return jsonify_msg('Wrong URL: "expression_id" should be an integer'), 400

    result = db.get_result(expression_id)
    if result[0].get('error_code') == 0:
        result = result[0].get('result')
        return jsonify({'result': result}), 200
    
    if result[0].get('error_code') == 1:
        result = 'ZeroDivisionError'
    if result[0].get('error_code') == 2:
        result = 'OverflowError'
    if result[0].get('error_code') == 3:
        result = 'Calculation TimeoutError'
    if result[0].get('error_code') == 4:
        result = 'Unexpected error'

    return jsonify_msg(result), 200
