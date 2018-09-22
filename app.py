import logging
import os
import requests
from flask import Flask, jsonify, abort, make_response, request

# Global Variables
API_KEY_YELP = os.environ['API_KEY_YELP']
headers = {'Authorization' : 'Bearer {0}'.format(
    API_KEY_YELP)}


# Helper Functions
def miles_to_meters(miles):
    '''
    Returns an int
    The Yelp API wants meters, but this API has an input in miles
    This API also only returns results up to a mile away
    One mile is 1609 meters
    '''
    if float(miles) >= 1:
        meters = 1609
    else:
        meters = int(float(miles) * 1609)

    return meters


# Functions that call the Yelp API
def get_categories():
    '''
    Returns a list
    List contains categories on success
    List contains error message on error
    '''
    categories = []

    base_url = 'https://api.yelp.com/v3/categories'
    # Only look for categories that apply to the US
    # Does this include of exclude blacklisted categories?
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


def get_businesses(latitude, longitude, radius, categories):
    '''
    Returns a list
    List contains dicts of business objects on success
    List contains error message on error
    '''
    businesses = []
    radius_meters = miles_to_meters(radius)

    base_url = 'https://api.yelp.com/v3/businesses/search'
    params = {'latitude' : latitude,
        'longitude' : longitude,
        'radius' : radius_meters,
        'categories' :  categories}

    print(params)

    try:
        r = requests.get(base_url, headers=headers, params=params)
        response = r.json()

        if r.status_code == 200:
            for business in response['businesses']:
                # Only return ten results
                # There is a parameter to limit the search results to ten
                # businesses, but the API does not guarantee that they're all in
                # the requested radius.
                # This way we do a little more work, but we can potentially return
                # more results in the requested radius rather than discarding
                # stuff from the first ten and leaving it at that
                if len(businesses) == 10:
                    break
                if business['distance'] > radius_meters:
                    logging.debug('{0} is {1} meters away, which is more than\
                        {2} meters, which was requested'.format(
                            business['name'], business['distance'], radius_meters))
                    continue
                
                new_business = {'id' : business['id'],
                    'name' : business['name'],
                    'coordinates' : business['coordinates']}

                businesses.append(new_business)
        else:
            logging.error('Received status code {0} from Yelp API with message:\n{1}'.format(
                r.status_code, response))
            businesses.append(response)

    except Exception as ex:
        logging.error('Could not connect to Yelp API with error:\n{0}'.format(
            str(ex)))
        businesses.append('Server could not communicate with Yelp API')

    return businesses


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


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'Error' : error.description}), 400)


@app.errorhandler(503)
def yelp_error(error):
    return make_response(jsonify({'Error' : error.description}), 503)


@app.route('/yelp/categories')
def publish_categories():
    categories = get_categories()
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
    print(categories)

    # Make sure the required parameters are present
    errors = {}
    if latitude == None:
        errors['Longitude'] = 'Longitude is a required parameter'
    if latitude == None:
        errors['Latitude'] = 'Latitude is a required parameter'
    if errors:
        abort(400, errors)

    businesses = get_businesses(latitude, longitude, radius, categories)
    if businesses[0] == 'Server could not communicate with Yelp API':
        abort(503, businesses[0])

    return jsonify({'data' : businesses})


@app.route('/yelp/businesses/details/<string:business_id>', methods=['GET'])
def publish_business_details(business_id):
    details = get_business_details(business_id)
    if details[0] == 'Server could not communicate with Yelp API':
        abort(503, categories[0])
    return jsonify({'data' : details})


if __name__ == '__main__':
    app.run(debug=True)
