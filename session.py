import flask

class Session(object):
    __SESSIONS = {}
    __CSRF_KEY = "google_auth_csrf_token"
    def __init__(self, credentials, accounts, user_file_path):
        self.credentials = credentials
        self.accounts = set(accounts)
        self.user_file_path = user_file_path

    def __add_account_id(self, id):
        self.accounts.add(id)
        self.__save_user_data()

    def __save_user_data(self):
        import json
        user_data = {
            "accounts": list(self.accounts)
        }
        with open(self.user_file_path, 'w') as fp:
            json.dump(user_data, fp)

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
    def store_user_credentials(cls, credentials, user_file_path):
        import uuid
        import json
        import os
        if os.path.exists(user_file_path):
            with open(user_file_path, 'r') as fp:
                user_data = json.load(fp)
        else:
            user_data = {
                "accounts": []
            }
            with open(user_file_path, 'w') as fp:
                json.dump(user_data, fp)

        session = cls(credentials, user_data["accounts"], user_file_path)

        guid = str(uuid.uuid4())
        flask.session["login_session_id"] = guid
        cls.__SESSIONS[guid] = session


    @classmethod
    def store_account_credentials(cls, credentials):
        login_session_id = flask.session["login_session_id"]
        cls.__SESSIONS[login_session_id].__add_account_id(credentials.id_token['sub'])

    @classmethod
    def get_login_credentials(cls):
        if "login_session_id" in flask.session:
            guid = flask.session["login_session_id"]
            credentials = cls.__SESSIONS[guid].credentials
            return credentials
        else:
            return None

    @classmethod
    def get_account_ids(cls):
        login_session_id = flask.session["login_session_id"]
        return cls.__SESSIONS[login_session_id].accounts

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
