import logging
import os
import requests
from flask import Flask, jsonify, abort, make_response

'''Global variables'''

API_KEY_YELP = os.environ['API_KEY_YELP']


app = Flask(__name__)

def get_categories():
    '''
    Returns a list of string
    List contains Yelp categories on success
    List contains error message on error
    '''

    categories = []

    url = 'https://api.yelp.com/v3/categories'
    headers = {'Authorization' : 'Bearer {0}'.format(
        API_KEY_YELP)}
    params = {'locale' : 'en_US'}

    try:
        r = requests.get(url, headers=headers, params=params)

        if r.status_code == 200:
            response = r.json()
            print('Got response')
            for category in response['categories']:
                categories.append(category['title'])
        else:
            logging.error('Received error {0} from Yelp API'.format(
                r.status_code))
            categories.append('Error connecting to Yelp API')
    
    except Exception as ex:
        logging.error('Could not connect to Yelp API with error:\n{0}'.format(
            str(ex)))
        categories.append('Error connecting to Yelp API')

    return categories


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/yelp/categories')
def publish_categories():
    categories = get_categories()
    return jsonify({'data' : categories})


if __name__ == '__main__':
    app.run(debug=True)
