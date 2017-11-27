import flask
import httplib2
from apiclient import discovery
import session
import flow_factory
import google_oauth

# creates a Flask application, named app
app = flask.Flask(__name__)

app.config['SECRET_KEY'] = '818d825f-f329-4b61-878a-7c5f138ba6a7'
app.config['GOOGLE_OAUTH2_CLIENT_ID'] = '816614257662-18mpfl219ag6f5de0v454ccpd8af9hr8.apps.googleusercontent.com'
app.config['GOOGLE_OAUTH2_CLIENT_SECRET'] = 'jxVpIi84T4LZCJLtBnP_MaVN'
app.config['GOOGLE_OAUTH2_SCOPES'] = ['profile', 'email']


login_oauth = google_oauth.GoogleOauth(app, ".credentials/client_secret.json",
                                 ['profile', 'email'],
                                 "login"
                                 )

account_oauth = google_oauth.GoogleOauth(app, ".credentials/client_secret.json",
                                 ['profile', 'email'],
                                 "account"
                                 )

# a route where we will display a welcome message via an HTML template
@app.route("/")
def index():
    if session.Session.is_user_logged_in():
        return flask.redirect(flask.url_for("accounts"))
    else:
        session.Session.start_login_flow()
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
    session.Session.start_account_flow()
    return flask.redirect(account_oauth.authorize_url(flask.url_for("index")), code=302)


@app.route('/accounts')
def accounts():
    # Create an httplib2.Http object to handle our HTTP requests and
    # authorize it with our good Credentials.
    login_credentials = session.Session.get_login_credentials()
    user = _get_profile(login_credentials)
    accounts = [_get_profile(credentials)
                for credentials in session.Session.get_account_credentials()]

    return flask.render_template("add_accounts.html", user=user, accounts=accounts)


# run the application
if __name__ == "__main__":

    app.run(debug=True, port=8081)

