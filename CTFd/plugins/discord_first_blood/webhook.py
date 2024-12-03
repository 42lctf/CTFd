from flask import request
from flask.wrappers import Response
from CTFd.utils.dates import ctftime
from CTFd.models import db, Challenges, Solves
from CTFd.utils import config as ctfd_config
from CTFd.utils.user import get_current_team, get_current_user
from functools import wraps
import requests
from requests.structures import CaseInsensitiveDict	

import re
from urllib.parse import quote
from types import SimpleNamespace
from flask import current_app

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
sanreg = re.compile(r'(~|!|@|#|\$|%|\^|&|\*|\(|\)|\_|\+|\`|-|=|\[|\]|;|\'|,|\.|\/|\{|\}|\||:|"|<|>|\?)')
sanitize = lambda m: sanreg.sub(r'\1',m)


url = current_app.config.get("DISCORD_URL")
headers = CaseInsensitiveDict()
headers["X-forwarded-IP"] = current_app.config.get("DISCORD_HOST")
headers["X-Secret"] = current_app.config.get("DISCORD_SECRET")
headers["X-Delivery"] = "ce que je veux"
headers["Content-Type"] = "application/json"

def load(app):
    TEAMS_MODE = ctfd_config.is_teams_mode()
   
    def challenge_attempt_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)
            # if not ctftime():
            #     return result
            if isinstance(result, Response):
                data = result.json
                if isinstance(data, dict) and data.get("success") == True and isinstance(data.get("data"), dict) and data.get("data").get("status") == "correct":
                    if request.content_type != "application/json":
                        request_data = request.form
                    else:
                        request_data = request.get_json()

                    challenge_id = request_data.get("challenge_id")
                    challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
                    
                    if (challenge.had_first_blood == True):
                        return result
                    challenge.had_first_blood = True
                    db.session.commit()

                    solvers = Solves.query.filter_by(challenge_id=challenge.id)
                    num_solves = solvers.count()

                    user = get_current_user()
                    team = get_current_team()

                    format_args = {
                        "team": sanitize("" if team is None else team.name),
                        "user_id": user.id,
                        "team_id": 0 if team is None else team.id,
                        "user": sanitize(user.name),
                        "challenge": sanitize(challenge.name),
                        "challenge_slug": quote(challenge.name),
                        "value": challenge.value,
                        "solves": num_solves,
                        "fsolves": ordinal(num_solves),
                        "category": sanitize(challenge.category)
                    }

                    print("FIRSTBLOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOD", format_args)
                    payload = {
                        "login": user.email.split("@")[0], 
                        "ctf_chall_details": {
                            "name": sanitize(challenge.name)},
                            "prod": 1 if (ctftime() and user.hidden == False) else 0
                    }
                    
                    resp = requests.post(url, headers=headers, json=payload)
                        
            return result
        return wrapper


    app.view_functions['api.challenges_challenge_attempt'] = challenge_attempt_decorator(app.view_functions['api.challenges_challenge_attempt'])
 
