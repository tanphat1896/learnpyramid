from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import (Everyone, Authenticated)

from .models import User


class MyAuth(AuthTktAuthenticationPolicy):
    def authenticated_userid(self, r):
        user = r.user
        if user is not None:
            return user.id
    def effective_principals(self, request):
        p = [Everyone]
        user = request.user
        if user is not None:
            p.append(Authenticated)
            p.append(str(user.id))
            p.append('role:' + user.role)
        return p

def getUser(r):
    id = r.unauthenticated_userid
    if id is not None:
        return r.dbsession.query(User).get(id)


def includeme(config):
    settings = config.get_settings()
    auth_policy = MyAuth(settings['auth.secret'], hashalg='sha512')
    config.set_authentication_policy(auth_policy)
    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.add_request_method(getUser, 'user', reify=True)
