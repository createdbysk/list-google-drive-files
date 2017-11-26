class FlowFactory(object):
    __INSTANCE = None
    def __init__(self):
        import flask
        from oauth2client.client import flow_from_clientsecrets
        self.flow = flow_from_clientsecrets('.credentials/client_secret.json',
                                          scope=['profile', 'email'],
                                           redirect_uri=flask.url_for('google_auth_return',
                                                                      _external=True))
    @classmethod
    def get_flow(cls):
        if cls.__INSTANCE is None:
            cls.__INSTANCE = cls()

        return cls.__INSTANCE.flow


