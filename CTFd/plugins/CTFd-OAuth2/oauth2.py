from flask import render_template, session, redirect
from flask_dance.consumer import OAuth2ConsumerBlueprint
import flask_dance.contrib
from flask import current_app

from CTFd.auth import confirm, register, reset_password, login
from CTFd.models import db, Users
from CTFd.utils import set_config, get_config
from CTFd.utils.logging import log
from CTFd.utils.security.auth import login_user, logout_user

from CTFd import utils

def load(app):
    ########################
    # Plugin Configuration #
    ########################
    
    authentication_url_prefix = "/auth"
    oauth2_client_id = current_app.config.get("OAUTH2_CLIENT_ID")
    oauth2_client_secret = current_app.config.get("OAUTH2_CLIENT_SECRET")
    
    oauth2_base_url = current_app.config.get("OAUTH2_BASE_URL")
    oauth2_token_url = current_app.config.get("OAUTH2_TOKEN_URL")
    oauth2_authorization_url = current_app.config.get("OAUTH2_AUTHORIZATION_URL")
    
    create_missing_user = True
    oauth_provider = 'oauth2'
    
    ##################
    # User Functions #
    ##################
    def retrieve_user_from_database(username):
        user = Users.query.filter_by(email=username).first()
        if user is not None:
            log('logins', "[{date}] {ip} - " + user.name + " - OAuth2 bridged user found")
            return user
    def create_user(username, displayName):
        with app.app_context():
            log('logins', "[{date}] {ip} - " + user.name + " - No OAuth2 bridged user found, creating user")
            user = Users(email=username, name=displayName.strip())
            db.session.add(user)
            db.session.commit()
            db.session.flush()
            return user
    def create_or_get_user(username, displayName):
        user = retrieve_user_from_database(username)
        if user is not None:
            return user
        if create_missing_user:
            return create_user(username, displayName)
        else:
            log('logins', "[{date}] {ip} - " + user.name + " - No OAuth2 bridged user found and not configured to create missing users")
            return None

    ##########################
    # Provider Configuration #
    ##########################
    provider_blueprints = {
        'oauth2': lambda: OAuth2ConsumerBlueprint(
            'oauth2', __name__,
            login_url='/oauth2',
            client_id=oauth2_client_id,
            client_secret=oauth2_client_secret,
            base_url=oauth2_base_url,
            token_url=oauth2_token_url,
            authorization_url=oauth2_authorization_url,
            redirect_url=authentication_url_prefix + "/oauth2/confirm"),
    }

    def get_oauth2_user():
        user_info = flask_dance.contrib.azure.azure.get("/v2/me").json()
        return create_or_get_user(
            username=user_info["email"],
            displayName=user_info["login"],
#            affiliation=f'{user_info["pool_year"]}.{user_info["pool_month"]}'),
        )

    provider_users = {
        'oauth2': lambda: get_oauth2_user()
    }

    provider_blueprint = provider_blueprints[oauth_provider]() # Resolved lambda
    
    #######################
    # Blueprint Functions #
    #######################
    @provider_blueprint.route('/<string:auth_provider>/confirm', methods=['GET'])
    def confirm_auth_provider(auth_provider):
        if not auth_provider in provider_users.keys():
            return redirect('/')

        provider_user = provider_users[oauth_provider]() # Resolved lambda
        session.regenerate()
        if provider_user is not None:
            login_user(provider_user)
        return redirect('/')

    app.register_blueprint(provider_blueprint, url_prefix=authentication_url_prefix)

    ###############################
    # Application Reconfiguration #
    ###############################
    # ('', 204) is "No Content" code
    # set_config('registration_visibility', False)
    app.view_functions['auth.oauth2'] = lambda: redirect(authentication_url_prefix + "/" + oauth_provider)
    # app.view_functions['auth.register'] = lambda: ('', 204)
    # app.view_functions['auth.reset_password'] = lambda: ('', 204)
    # app.view_functions['auth.confirm'] = lambda: ('', 204)     
