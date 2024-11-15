from CTFd.constants.config import (
    AccountVisibilityTypes,
    ChallengeVisibilityTypes,
    ConfigTypes,
    RegistrationVisibilityTypes,
    ScoreVisibilityTypes,
)
from CTFd.utils import get_config
from CTFd.utils.user import authed, is_admin

def challenges_visible():
    v = get_config(ConfigTypes.CHALLENGE_VISIBILITY)
    if v == ChallengeVisibilityTypes.PUBLIC:
        return True
    elif v == ChallengeVisibilityTypes.PRIVATE or v == ChallengeVisibilityTypes.PRIVATE_PO:
        return authed()
    elif v == ChallengeVisibilityTypes.ADMINS:
        return is_admin()

def challenges_po_mode():
    v = get_config(ConfigTypes.CHALLENGE_VISIBILITY)
    return v == ChallengeVisibilityTypes.PRIVATE_PO


def scores_visible():
    v = get_config(ConfigTypes.SCORE_VISIBILITY)
    if v == ScoreVisibilityTypes.PUBLIC:
        return True
    elif v == ScoreVisibilityTypes.PRIVATE:
        return authed()
    elif v == ScoreVisibilityTypes.HIDDEN:
        return False
    elif v == ScoreVisibilityTypes.ADMINS:
        return is_admin()


def accounts_visible():
    v = get_config(ConfigTypes.ACCOUNT_VISIBILITY)
    if v == AccountVisibilityTypes.PUBLIC:
        return True
    elif v == AccountVisibilityTypes.PRIVATE:
        return authed()
    elif v == AccountVisibilityTypes.ADMINS:
        return is_admin()


def registration_visible():
    v = get_config(ConfigTypes.REGISTRATION_VISIBILITY)
    if v == RegistrationVisibilityTypes.PUBLIC:
        return True
    elif v == RegistrationVisibilityTypes.PRIVATE:
        return False
    else:
        return False
    
def direct_login_visible():
    v = get_config(ConfigTypes.DIRECT_LOGIN_VISIBILITY)
    return v == 'visible'

def oauth_login_visible():
    v = get_config(ConfigTypes.OAUTH2_LOGIN_VISIBILITY)
    return v == 'visible'

def po_login_visible():
    v = get_config(ConfigTypes.PO_LOGIN_VISIBILITY)
    return v == 'visible'
