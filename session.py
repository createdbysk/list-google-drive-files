import flask

class Session(object):
    __SESSIONS = {}
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

