import flask
from oauth2client.contrib.flask_util import UserOAuth2
import httplib2
from apiclient import discovery
import session
import flow_factory

# creates a Flask application, named app
app = flask.Flask(__name__)

app.config['SECRET_KEY'] = '818d825f-f329-4b61-878a-7c5f138ba6a7'
app.config['GOOGLE_OAUTH2_CLIENT_ID'] = '816614257662-18mpfl219ag6f5de0v454ccpd8af9hr8.apps.googleusercontent.com'
app.config['GOOGLE_OAUTH2_CLIENT_SECRET'] = 'jxVpIi84T4LZCJLtBnP_MaVN'
app.config['GOOGLE_OAUTH2_SCOPES'] = ['profile', 'email']
# oauth2 = UserOAuth2(app, include_granted_scopes="true")

# a route where we will display a welcome message via an HTML template
@app.route("/")
def index():
    if session.Session.is_user_logged_in():
        return _display_info()
    else:
        session.Session.start_login_flow()
        return flask.redirect(flask.url_for("login"))

@app.route("/login")
def login():
    return flask.render_template('login.html')

@app.route("/logout")
def logout():
    flask.session.pop("session_id", None)
    return flask.redirect(flask.url_for("index"))

@app.route("/google/oauth")
def google_oauth():
    csrf_token = session.Session.generate_csrf_token()
    flow = flow_factory.FlowFactory.get_flow()
    authorize_url = flow.step1_get_authorize_url(state=csrf_token)
    return flask.redirect(authorize_url, code=302)


@app.route("/google_auth_return")
def google_auth_return():
    code = flask.request.args.get('code')
    csrf_token = flask.request.args.get('state')
    if session.Session.is_csrf_token_valid(csrf_token):
        flow = flow_factory.FlowFactory.get_flow()
        credentials = flow.step2_exchange(code)
        session.Session.store_credentials(credentials)
        return _display_info()
    else:
        return flask.redirect(flask.url_for("index"), code=302)

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

def _display_info():
    # Create an httplib2.Http object to handle our HTTP requests and
    # authorize it with our good Credentials.
    login_credentials = session.Session.get_login_credentials()
    user = _get_profile(login_credentials)
    accounts = [_get_profile(credentials)
                for credentials in session.Session.get_account_credentials()]

    return flask.render_template("add_accounts.html", user=user, accounts=accounts)


@app.route('/add_account')
def add_account():
    session.Session.start_account_flow()
    return flask.redirect(flask.url_for("google_oauth"), code=302)


# run the application
if __name__ == "__main__":

    app.run(debug=True, port=8081)

