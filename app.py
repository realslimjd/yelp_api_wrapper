import logging
import os
import requests
from flask import Flask, jsonify, abort, make_response, request

# Global Variables
API_KEY_YELP = os.environ['API_KEY_YELP']
headers = {'Authorization' : 'Bearer {0}'.format(
    API_KEY_YELP)}


# Helper Functions
def get_categories():
    '''
    Returns a list of string
    List contains Yelp categories on success
    List contains error message on error
    '''

    categories = []

    base_url = 'https://api.yelp.com/v3/categories'
    params = {'locale' : 'en_US'}

    try:
        r = requests.get(base_url, headers=headers, params=params)
        response = r.json()

        if r.status_code == 200:
            for category in response['categories']:
                categories.append(category['title'])
        else:
            logging.error('Received status code {0} from Yelp API with message:\n{1}'.format(
                r.status_code, response))
            categories.append(response)
    
    except Exception as ex:
        logging.error('Could not connect to Yelp API with error:\n{0}'.format(
            str(ex)))
        categories.append('Server could not communicate with Yelp API')

    return categories


def get_business_details(business_id):
    '''
    Returns a list
    List contains a dict all business details from Yelp on success
    List contains error message on error
    '''

    details = []

    base_url = 'https://api.yelp.com/v3/businesses/'
    query_url = base_url + business_id

    try:
        r = requests.get(query_url, headers=headers)
        response = r.json()

        if r.status_code == 200:
            details.append(response)
        else:
            logging.error('Received status code {0} from Yelp API with message:\n{1}'.format(
                r.status_code, response))
            details.append(response)

    except Exception as ex:
        logging.error('Could not connect to Yelp API with error:\n{0}'.format(
            str(ex)))
        details.append('Server could not communicate with Yelp API')

    return details


# The Flask-y part
app = Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'Error' : error.description}), 404)


@app.errorhandler(503)
def yelp_error(error):
    return make_response(jsonify({'Error' : error.description}), 503)


@app.route('/yelp/categories')
def publish_categories():
    categories = get_categories()
    if categories[0] == 'Server could not communicate with Yelp API':
        abort(503, categories[0])
    return jsonify({'data' : categories})


@app.route('/yelp/businesses/details/<string:business_id>', methods=['GET'])
def publish_business_details(business_id):
    details = get_business_details(business_id)
    if details[0] == 'Server could not communicate with Yelp API':
        abort(503, categories[0])
    return jsonify({'data' : details})


if __name__ == '__main__':
    app.run(debug=True)
