from flask import Flask, jsonify, request, abort
###
from utils.helpers import ssl_required
from utils.NYCCitiBikeParser import NYCCitiBikeParser
from utils.NYCCitiBikeParserExceptions import NYCCitiBikeLoginError

app = Flask(__name__)


@app.route('/trips', methods=['POST'])
@ssl_required
def get_trips():

    # 'username' and 'password' are required
    if 'username' not in request.form or 'password' not in request.form:
        abort(400, "Must supply 'username' and 'password'")

    username = request.form['username']
    password = request.form['password']

    try:

        # attempt to login
        nyc_citibike_parser = NYCCitiBikeParser(username, password)

        # get the trips
        trips = nyc_citibike_parser.get_trips()

        # return the trips
        return jsonify({
            'data': {
                'trips': trips
            }
        })

    except NYCCitiBikeLoginError:
        abort(403, "Could not log in with those credentials")

    abort(500, "An unknown error occurred")


@app.route('/verify-login', methods=['POST'])
@ssl_required
def verify_login():

    # 'username' and 'password' are required
    if 'username' not in request.form or 'password' not in request.form:
        abort(400, "Must supply 'username' and 'password'")

    username = request.form['username']
    password = request.form['password']

    try:

        # attempt to login
        NYCCitiBikeParser(username, password)

        return "Success"

    except NYCCitiBikeLoginError:
        abort(403, "Could not log in with those credentials")

    abort(500, "An unknown error occurred")

if __name__ == '__main__':
    app.debug = True
    app.run()