import flask

class Session(object):
    __SESSIONS = {}
    __CSRF_KEY = "google_auth_csrf_token"
    def __init__(self, credentials):
        self.credentials = credentials
        self.accounts = {}

    @classmethod
    def is_user_logged_in(cls):
        if "login_session_id" in flask.session:
            guid = flask.session["login_session_id"]
            if guid in cls.__SESSIONS:
                return True

        return False

    @classmethod
    def logout(cls):
        flask.session.pop("login_session_id", None)

    @classmethod
    def start_login_flow(cls):
        flask.session["login_flow"] = True
        flask.session.pop("account_flow", None)

    @classmethod
    def start_account_flow(cls):
        flask.session["account_flow"] = True
        flask.session.pop("login_flow", None)

    @classmethod
    def store_credentials(cls, credentials):
        import uuid
        guid = str(uuid.uuid4())
        session = cls(credentials)
        if "login_flow" in flask.session:
            flask.session["login_session_id"] = guid
            flask.session.pop("login_flow", None)
            cls.__SESSIONS[guid] = session
            return "login_flow"
        elif "account_flow" in flask.session:
            flask.session.pop("account_flow", None)
            login_session_id = flask.session["login_session_id"]
            cls.__SESSIONS[login_session_id].accounts[guid] = session
            return "account_flow"
        return None

    @classmethod
    def get_login_credentials(cls):
        if "login_session_id" in flask.session:
            guid = flask.session["login_session_id"]
            credentials = cls.__SESSIONS[guid].credentials
            return credentials
        else:
            return None

    @classmethod
    def get_account_credentials(cls):
        login_session_id = flask.session["login_session_id"]
        for guid, session in cls.__SESSIONS[login_session_id].accounts.iteritems():
            yield session.credentials

    @classmethod
    def generate_csrf_token(cls):
        import hashlib
        import os
        csrf_token = hashlib.sha256(os.urandom(1024)).hexdigest()
        flask.session[cls.__CSRF_KEY] = csrf_token
        return csrf_token

    @classmethod
    def is_csrf_token_valid(cls, csrf_token):
        if cls.__CSRF_KEY in flask.session:
            stored_csrf_token = flask.session[cls.__CSRF_KEY]
            return stored_csrf_token == csrf_token

        return False
