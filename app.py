'''
This file contains all the routing information for the API.
There's also a little error handling as well.
Calls to the Yelp API are handlded in calls.py
'''
import logging
from api_calls import calls as y_api
from flask import Flask, jsonify, abort, make_response, request


# The Flask-y part
app = Flask(__name__)


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'Error' : error.description}), 400)


@app.errorhandler(503)
def yelp_error(error):
    return make_response(jsonify({'Error' : error.description}), 503)


@app.route('/yelp/categories')
def publish_categories():
    categories = y_api.get_categories()
    if categories[0] == 'Server could not communicate with Yelp API':
        abort(503, categories[0])
    return jsonify({'data' : categories})


@app.route('/yelp/businesses/search')
def publish_business_list():
    # Get the paramaters
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    radius = request.args.get('radius', 1)
    categories = request.args.get('categories')

    # Make sure the required parameters are present
    errors = {}
    if latitude == None:
        errors['Longitude'] = 'Longitude is a required parameter'
    if latitude == None:
        errors['Latitude'] = 'Latitude is a required parameter'
    if errors:
        abort(400, errors)

    businesses = y_api.get_businesses(latitude, longitude, radius, categories)
    if businesses[0] == 'Server could not communicate with Yelp API':
        abort(503, businesses[0])

    return jsonify({'data' : businesses})


@app.route('/yelp/businesses/details/<string:business_id>', methods=['GET'])
def publish_business_details(business_id):
    details = y_api.get_business_details(business_id)
    if details[0] == 'Server could not communicate with Yelp API':
        abort(503, categories[0])
    return jsonify({'data' : details})


if __name__ == '__main__':
    app.run(debug=True)
