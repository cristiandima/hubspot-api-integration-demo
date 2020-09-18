from flask import render_template


class OAuthError(Exception):
    def __init__(self, message=None):
        Exception.__init__(self)
        self.message = message


def handle_oauth_error(e):
    return render_template('errors/error.html', e=e), 500
