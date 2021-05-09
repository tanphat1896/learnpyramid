from pyramid.httpexceptions import HTTPFound
from pyramid.security import (remember, forget)
from pyramid.view import (view_config, forbidden_view_config)
from ..models import User

@view_config(route_name="login", renderer="../templates/login.jinja2")
def login(r):
    print r.context
    ms = ''
    login = ''
    if ('form.submitted' in r.params):
        login = r.params['login']
        password = r.params['password']
        user = r.dbsession.query(User).filter_by(name=login).first()
        if (user is not None and user.check_password(password)):
            headers = remember(r, user.id)
            print "Headers: ", headers
            return HTTPFound(location=r.route_url('view_wiki'), headers=headers)
        ms = 'Invalid login'

    return dict(
        message=ms,
        url=r.route_url('login'),
        login=login
    )

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    print "Headers: ", headers
    next_url = request.route_url('view_wiki')
    return HTTPFound(location=next_url, headers=headers)

@forbidden_view_config()
def forbidden_view(request):
    next_url = request.route_url('login', _query={'next': request.url})
    return HTTPFound(location=next_url)

