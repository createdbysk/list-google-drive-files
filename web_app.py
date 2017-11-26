import flask
from oauth2client.contrib.flask_util import UserOAuth2
import httplib2
from apiclient import discovery
from oauth2client.file import Storage
import os

# creates a Flask application, named app
app = flask.Flask(__name__)

app.config['SECRET_KEY'] = '818d825f-f329-4b61-878a-7c5f138ba6a7'
app.config['GOOGLE_OAUTH2_CLIENT_ID'] = '816614257662-18mpfl219ag6f5de0v454ccpd8af9hr8.apps.googleusercontent.com'
app.config['GOOGLE_OAUTH2_CLIENT_SECRET'] = 'jxVpIi84T4LZCJLtBnP_MaVN'
app.config['GOOGLE_OAUTH2_SCOPES'] = ['drive.metadata.readonly']
oauth2 = UserOAuth2()

def _request_user_info(credentials):
    # Create an httplib2.Http object to handle our HTTP requests and
    # authorize it with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Build a service object for interacting with the API.
    #people_service = discovery.build(serviceName='people', version='v1', http=http)
    #raw_profile = people_service.people().get(resourceName='people/me',
    #                                      personFields='names,emailAddresses,photos').execute()
    #profile = {
    #    "name": raw_profile["names"][0]["displayName"],
    #    "email": raw_profile["emailAddresses"][0]["value"],
    #    "image": raw_profile["photos"][0]["url"]
    #}
    #flask.session['profile'] = profile


home_dir = os.path.expanduser('~')
credential_dir = os.path.join(home_dir, '.credentials')
if not os.path.exists(credential_dir):
    os.makedirs(credential_dir)
credential_path = os.path.join(credential_dir,
                               'drive-python-{suffix}.json'.format(suffix='main1'))

store = Storage(credential_path)

oauth2.init_app(
    app,
    scopes=['email', 'profile'],
    authorize_callback=_request_user_info,
    storage=store)

# a route where we will display a welcome message via an HTML template
@app.route("/")
def index():
    if oauth2.has_credentials():
        return flask.redirect(flask.url_for("add_accounts"))
    else:
        return flask.redirect(flask.url_for("login"))

@app.route("/login")
def login():
    return flask.render_template('login.html')

@app.route("/logout")
def logout():
    import requests
    flask.session.pop('profile', None)
    flask.session.modified = True
    credentials = oauth2.credentials
    requests.post(credentials.revoke_uri,
                  params={'token': credentials.access_token},
                  headers={'content-type': 'application/x-www-form-urlencoded'})
    store.delete()
    return flask.redirect(flask.url_for("index"))

@app.route("/google/oauth")
def google_oauth():
    return flask.redirect(oauth2.authorize_url(flask.url_for("index")))

@app.route('/add_accounts')
@oauth2.required
def add_accounts():
    return flask.render_template("add_accounts.html")

# run the application
if __name__ == "__main__":

    app.run(debug=True, port=8081)

