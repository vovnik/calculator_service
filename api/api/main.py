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
db.migrate()

# Error messages for results with error codes 
ERROR_MESSAGES = ['', 'ZeroDivisionError',    #error_code 1
               'OverflowError',               #error_code 2
               'Calculation TimeoutError',    #error_code 3
               'Unexpected error']            #error code 4 

def jsonify_msg(msg: str):
    return jsonify({"msg": msg})


def signal_handler(signum, frame):
    raise TimeoutError("Calculation takes to long!")

@app.route("/")
def index():
    return "<h1>index test</h1>"

@app.route("/api/expression", methods=['POST'])
def post_expression():
    try:
        raw_json = request.get_json()
        expression = raw_json['expression']
        variables = raw_json['variables']
    except TypeError:
        return jsonify_msg('No JSON found'), 400
    except KeyError:
        return jsonify_msg('JSON has a wrong structure'), 400

    try:
        parser = Parser()
        # mathematical expression validation (yes, we expect hackers in our network)
        parsed_expression = parser.parse(expression)
    # "py_expression_eval" uses Exception class for all exceptions except devision by zero and overflow :(
    except Exception:
        return jsonify_msg('Error occured while parsing expression'), 400

    # variables matching validation
    variables_set = set(parsed_expression.variables())
    if variables_set != set(variables):
        return jsonify_msg('JSON["variables"] does not match with variables in expression'), 400

    expression_id = db.put_task(expression, variables)
    return jsonify(expression_id[0]), 200


@app.route("/api/result/<expression_id>", methods=['GET'])
def get_expression_result(expression_id):
    try:
        expression_id = int(expression_id)
    except ValueError as e:
        logger.warning(e)
        return jsonify_msg('Wrong URL: "expression_id" should be an integer'), 400

    result = db.get_result(expression_id)
    if len(result) == 0:
        return jsonify_msg('Currently there is no such result'), 204

    error_code = result[0].get('error_code')
    if error_code == 0:
        result = result[0].get('result')
        return jsonify({'result': result}), 200

    result = ERROR_MESSAGES[error_code]
    return jsonify_msg(result), 200
