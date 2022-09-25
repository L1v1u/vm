"""Various helpers for auth. Mainly about tokens blocklisting

Heavily inspired by
https://github.com/vimalloc/flask-jwt-extended/blob/master/examples/blocklist_database.py
"""
from datetime import datetime

from flask_jwt_extended import decode_token
from sqlalchemy.orm.exc import NoResultFound

from vm.extensions import db
from vm.models import TokenBlocklist


def add_token_to_database(encoded_token, identity_claim):
    """
    Adds a new token to the database. It is not revoked when it is added.

    :param identity_claim: configured key to get user identity
    """
    decoded_token = decode_token(encoded_token)
    jti = decoded_token["jti"]
    token_type = decoded_token["type"]
    user_identity = decoded_token[identity_claim]
    expires = datetime.fromtimestamp(decoded_token["exp"])
    revoked = False

    db_token = TokenBlocklist(
        jti=jti,
        token_type=token_type,
        user_id=user_identity,
        expires=expires,
        revoked=revoked,
    )
    db.session.add(db_token)
    db.session.commit()


def is_token_revoked(jwt_payload):
    """
    Checks if the given token is revoked or not. Because we are adding all the
    tokens that we create into this database, if the token is not present
    in the database we are going to consider it revoked, as we don't know where
    it was created.
    """
    jti = jwt_payload["jti"]
    try:
        token = TokenBlocklist.query.filter_by(jti=jti).one()
        return token.revoked
    except NoResultFound:
        return True


def revoke_token(token_jti, user):
    """Revokes the given token

    Since we use it only on logout that already require a valid access token,
    if token is not found we raise an exception
    """
    try:
        token = TokenBlocklist.query.filter_by(jti=token_jti, user_id=user).one()
        token.revoked = True
        db.session.commit()
    except NoResultFound:
        raise Exception("Could not find the token {}".format(token_jti))


def revoke_all_tokens(user):
    """Revokes all token for user

    Since we use it only on logout that already require a valid access token,
    if token is not found we raise an exception
    """
    try:
        tokens = TokenBlocklist.query.filter_by(user_id=user).all()
        for token in tokens:
            token.revoked = True
            db.session.add(token)
        db.session.commit()
    except NoResultFound:
        raise Exception(f"Could not find the user {user}")


def has_other_tokens(user):
    """ Check active tokens not revoked for a specific user

    In case the are not revoked and we divide by 2 for every user there is,
    access and refresh token in the db
    """
    try:
        return TokenBlocklist.query.filter_by(user_id=user, revoked=False).count()/2 > 1
    except NoResultFound:
        raise Exception(f"Could not find the user {user}")
