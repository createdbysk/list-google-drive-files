import os
import flask
import httplib2
from apiclient import discovery
import session
import google_oauth
import uuid
from oauth2client.contrib.multiprocess_file_storage import MultiprocessFileStorage

# creates a Flask application, named app
app = flask.Flask(__name__)

app.config['SECRET_KEY'] = str(uuid.uuid4())

def __get_users_dir():
    home_dir = os.path.expanduser('~')
    users_dir = os.path.join(home_dir, '.users')
    if not os.path.exists(users_dir):
        os.makedirs(users_dir)
    return users_dir

def __get_credentials_file_path():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-multiprocessfilestorage.json')
    return credential_path

def store_user(credentials):
    id = credentials.id_token['sub']
    users_dir = __get_users_dir()
    user_file_path = os.path.join(users_dir, 'drive-python-user-{id}.json'.format(id=id))
    session.Session.store_user_credentials(credentials, user_file_path)


def store_account_credentials(credentials):
    session.Session.store_account_credentials(credentials)
    id = credentials.id_token['sub']
    storage = MultiprocessFileStorage(__get_credentials_file_path(), id)
    storage.put(credentials)
    credentials.set_store(storage)

login_oauth = google_oauth.GoogleOauth(app, ".credentials/client_secret.json",
                                 ['profile', 'email'],
                                 "login",
                                 store_user
                                 )

account_oauth = google_oauth.GoogleOauth(app, ".credentials/client_secret.json",
                                         ['profile', 'email'],
                                         "account",
                                         store_account_credentials
                                         )


# a route where we will display a welcome message via an HTML template
@app.route("/")
def index():
    if session.Session.is_user_logged_in():
        return flask.redirect(flask.url_for("accounts_view"))
    else:
        return flask.redirect(flask.url_for("login"))


@app.route("/login")
def login():
    return flask.render_template('login.html',
                                 login_authorize_url=login_oauth.authorize_url(flask.url_for("index")))


@app.route("/logout")
def logout():
    session.Session.logout()
    return flask.redirect(flask.url_for("index"))


def _get_profile(credentials):
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Build a service object for interacting with the API.
    people_service = discovery.build(serviceName='people', version='v1', http=http)
    profile = people_service.people().get(resourceName='people/me',
                                          personFields='names,emailAddresses').execute()
    user = {
        "name": profile["names"][0]["displayName"],
        "email": profile["emailAddresses"][0]["value"],
        "id": profile["names"][0]["metadata"]["source"]["id"]
    }

    return user


@app.route('/add_account')
def add_account():
    return flask.redirect(account_oauth.authorize_url(flask.url_for("index")), code=302)


@app.route('/accounts')
def accounts_view():
    # Create an httplib2.Http object to handle our HTTP requests and
    # authorize it with our good Credentials.
    login_credentials = session.Session.get_login_credentials()
    user = _get_profile(login_credentials)
    accounts = []
    for id in session.Session.get_account_ids():
        credentials = MultiprocessFileStorage(__get_credentials_file_path(), id).get()
        accounts.append({"id": credentials.id_token['sub'],
                         "email": credentials.id_token['email']})

    return flask.render_template("add_accounts.html", user=user, accounts=accounts)


# run the application
if __name__ == "__main__":

    app.run(debug=True, port=8081)

