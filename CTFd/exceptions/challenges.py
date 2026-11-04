"""Rétroportage de CTFd/exceptions/challenges.py, apparu en CTFd 3.7.6.

Le plugin `containers` importe ces deux exceptions (son __init__.py ligne 15) et
les lève à la création et à la mise à jour d'un challenge. Sur CTFd 3.7.4 le
module n'existe pas, ce qui provoque un ImportError au chargement du plugin.

Les classes amont ne contiennent rien d'autre que `pass` ; ce fichier en est la
copie fidèle, et non une adaptation.

Limite connue : en 3.7.6 l'API challenges rattrape ces exceptions pour renvoyer
un message lisible. En 3.7.4, CTFd/api/v1/challenges.py appelle
`challenge_class.create(request)` sans try/except, donc une saisie invalide dans
le formulaire d'administration remonte en HTTP 500 au lieu d'une erreur claire.
Cela ne concerne que l'administration, jamais les joueurs. À supprimer lors de
la montée en 3.7.6 ou ultérieur.
"""


class ChallengeCreateException(Exception):
    pass


class ChallengeUpdateException(Exception):
    pass
