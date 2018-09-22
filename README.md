## Instructions
Notes: Tested on macOS 10.13 with Python 3.7. Should be compatible with Linux and Python >= 3.0

### Prerequisites
* [Python 3](http://docs.python-guide.org/en/latest/)
* [Pip](https://pip.pypa.io/en/stable/installing/)
* [Virtualenv](https://virtualenv.pypa.io/en/stable/installation/)
* [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

### How to run this application:
1. Make sure you have all the prerequisites installed. If not, follow the linked instructions above for how to install them.
2. Clone this directory into a new folder.
3. In the project directory, create a new virtualenv with the command `virtualenv -p python3 env`
4. Activate the virtualenv with `source env/bin/activate`
5. Install the dependencies by running `pip install -r requirements.txt`
6. Enter the API key by running `export API_KEY_YELP=$YOUR_KEY`
7. Start the app with `python app.py`
8. Open your web browser and navigate to <http://127.0.0.1:5000/api_endpoint>
9. (Be patient)
10. Results! (Hopefully)
11. You can stop the Flask server by hitting `Ctrl+C`
12. Close the virtualenv with the command `deactivate`
