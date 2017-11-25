from flask import Flask
from flask import render_template
from oauth2client.client import flow_from_clientsecrets
from oauth2client.contrib.flask_util import UserOAuth2

# creates a Flask application, named app
app = Flask(__name__)

app.config['SECRET_KEY'] = '818d825f-f329-4b61-878a-7c5f138ba6a7'
app.config['GOOGLE_OAUTH2_CLIENT_ID'] = '816614257662-18mpfl219ag6f5de0v454ccpd8af9hr8.apps.googleusercontent.com'
app.config['GOOGLE_OAUTH2_CLIENT_SECRET'] = 'jxVpIi84T4LZCJLtBnP_MaVN'
oauth2 = UserOAuth2(app)

flow = flow_from_clientsecrets('.credentials/client_secret.json',
                               scope='https://www.googleapis.com/auth/drive.metadata.readonly',
                               redirect_uri='http://localhost:8081/auth_return')


# a route where we will display a welcome message via an HTML template
@app.route("/")
def hello():
    return render_template('index.html')


@app.route("/main")
@oauth2.required
def call_main():
    from flask import redirect
    authorize_url = flow.step1_get_authorize_url()
    return redirect(authorize_url, code=302)


@app.route("/auth_return")
def call_auth_return():
    from flask import request
    import main
    code = request.args.get('code')
    credentials = flow.step2_exchange(code)
    main.add_to_object_store(credentials)
    return 'Success'


# run the application
if __name__ == "__main__":

    app.run(debug=True, port=8081)

