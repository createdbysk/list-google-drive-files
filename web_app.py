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
oauth2 = UserOAuth2(app, include_granted_scopes="true")

# a route where we will display a welcome message via an HTML template
@app.route("/")
def index():
    if oauth2.has_credentials():
        return flask.redirect(flask.url_for("add_accounts"))
    else:
        return flask.redirect(flask.url_for("login"))

    #if session.Session.is_user_logged_in():
    #    return flask.redirect(flask.url_for("add_accounts"))
    #else:
    #    return flask.redirect(flask.url_for("login"))

@app.route("/login")
def login():
    return flask.render_template('login.html')

@app.route("/logout")
def logout():
    #flask.session.pop("session_id", None)
    #return flask.redirect(flask.url_for("index"))
    # Delete the user's profile and the credentials stored by oauth2.
    flask.session.pop('profile', None)
    flask.session.modified = True
    oauth2.storage.delete()
    return flask.redirect(flask.url_for("index"))

@app.route("/google/oauth")
def google_oauth():
    return flask.redirect(oauth2.authorize_url("/add_accounts"))
    #flow = flow_factory.FlowFactory.get_flow()
    #authorize_url = flow.step1_get_authorize_url()
    #return flask.redirect(authorize_url, code=302)


@app.route("/google_auth_return")
def google_auth_return():
    code = flask.request.args.get('code')
    flow = flow_factory.FlowFactory.get_flow()
    credentials = flow.step2_exchange(code)
    session.Session.store_credentials(credentials)
    return flask.redirect(flask.url_for("add_accounts"))

@app.route('/add_accounts')
@oauth2.required
def add_accounts():
    #credentials = session.Session.get_credentials()
    #credentials = oauth2.credentials
    #if credentials:
    # Create an httplib2.Http object to handle our HTTP requests and
    # authorize it with our good Credentials.
    #http = httplib2.Http()
    #http = credentials.authorize(http)

    # Build a service object for interacting with the API.
    #people_service = discovery.build(serviceName='people', version='v1', http=http)
    #profile = people_service.people().get(resourceName='people/me',
    #                                      personFields='names,emailAddresses').execute()
    user = {
        "name": oauth2.user_id,
#profile["names"][0]["displayName"],
        "email_address": oauth2.email
#profile["emailAddresses"][0]["value"]
    }
    return flask.render_template("add_accounts.html", user=user)
#else:
#    return flask.redirect(flask.url_for("index"), code=302)

# run the application
if __name__ == "__main__":

    app.run(debug=True, port=8081)

