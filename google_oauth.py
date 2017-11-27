import flask


class GoogleOauth(object):
    def __init__(self, app, client_secret_file, scopes, url_prefix, authorize_callback=None):
        self.__app = app
        self.__client_secret_file = client_secret_file
        self.__scopes = scopes
        self.__url_prefix = url_prefix
        self.__flow = None
        self.__authorize_callback = authorize_callback
        self.__init_app()

    def __init_app(self):
        blueprint = self.__create_blueprint()
        self.__app.register_blueprint(blueprint,
                                      url_prefix="/{url_prefix}".format(
                                          url_prefix=self.__url_prefix
                                      ))

    def authorize_url(self, return_url, **kwargs):
        return flask.url_for(self.build_endpoint("authorize"), return_url=return_url, **kwargs)

    def build_endpoint(self, endpoint):
        return "{url_prefix}.{endpoint}".format(
            url_prefix=self.__url_prefix,
            endpoint=endpoint
        )

    def __create_blueprint(self):
        blueprint = flask.Blueprint(self.__url_prefix, __name__)
        blueprint.add_url_rule("/google/oauth2authorize", "authorize", self.__authorize_view)
        blueprint.add_url_rule("/google/oauth2callback", "callback", self.__callback_view)
        return blueprint

    def __get_flow(self):
        if not self.__flow:
            from oauth2client.client import flow_from_clientsecrets
            self.__flow = flow_from_clientsecrets(self.__client_secret_file,
                                                  scope=self.__scopes,
                                                  redirect_uri=flask.url_for(self.build_endpoint("callback"),
                                                                             _external=True))
        return self.__flow

    def __authorize_view(self):
        import session
        import json
        args = flask.request.args.to_dict()

        return_url = args.pop('return_url', None)
        if return_url is None:
            return_url = flask.request.referrer or '/'

        csrf_token = session.Session.generate_csrf_token()
        flow = self.__get_flow()
        state = json.dumps({
            "csrf_token": csrf_token,
            "return_url": return_url
        })

        authorize_url = flow.step1_get_authorize_url(state=state)
        return flask.redirect(authorize_url, code=302)

    def __callback_view(self):
        import session
        import json
        try:
            code = flask.request.args.get('code')
            encoded_state = flask.request.args.get('state')
            state = json.loads(encoded_state)
            csrf_token = state["csrf_token"]
            return_url = state["return_url"]
            if session.Session.is_csrf_token_valid(csrf_token):
                flow = self.__get_flow()
                credentials = flow.step2_exchange(code)
                session.Session.store_credentials(credentials)
                if self.__authorize_callback:
                    self.__authorize_callback(credentials)
            return flask.redirect(return_url)
        except (ValueError, KeyError):
            return "Invalid request state", 400
