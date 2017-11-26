import flask

class Session(object):
    __SESSIONS = {}
    __CSRF_KEY = "google_auth_csrf_token"
    def __init__(self, credentials):
        self.credentials = credentials

    @classmethod
    def is_user_logged_in(cls):
        if "session_id" in flask.session:
            guid = flask.session["session_id"]
            if guid in cls.__SESSIONS:
                return True

        return False

    @classmethod
    def store_credentials(cls, credentials):
        import uuid
        guid = str(uuid.uuid4())
        session = cls(credentials)
        cls.__SESSIONS[guid] = session
        flask.session["session_id"] = guid

    @classmethod
    def get_credentials(cls):
        if "session_id" in flask.session:
            guid = flask.session["session_id"]
            credentials = cls.__SESSIONS[guid].credentials
            return credentials
        else:
            return None

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
