from pyramid.compat import escape
import re
from docutils.core import publish_parts

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    HTTPForbidden
)

from pyramid.view import view_config

from ..models import Page, User

# regular expression used to find WikiWords
wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")


@view_config(route_name="view_wiki")
def viewWiki(r):
    url = r.route_url('view_page', pagename='FrontPage')
    return HTTPFound(url)


@view_config(route_name="view_page", renderer="../templates/view.jinja2", permission="view")
def viewPage(r):
    page = r.context.page
    if page is None:
        return HTTPNotFound("Page %s not found" % pagename)

    def add_link(match):
        word = match.group(1)
        print word
        exists = r.dbsession.query(Page).filter_by(name=word).all()
        if exists:
            view_url = r.route_url('view_page', pagename=word)
            return '<a href="%s">%s</a>' % (view_url, escape(word))
        else:
            add_url = r.route_url('add_page', pagename=word)
            return '<a href="%s">%s</a>' % (add_url, escape(word))

    content = publish_parts(page.data, writer_name='html')['html_body']
    content = wikiwords.sub(add_link, content)
    edit_url = r.route_url('edit_page', pagename=page.name)
    return dict(page=page, content=content, edit_url=edit_url)


@view_config(route_name="edit_page", renderer="../templates/edit.jinja2", permission="edit")
def editPage(r):
    page = r.context.page
    user = r.user
    if user is None or (user.role != 'editor' and page.creator != user):
        raise HTTPForbidden
    if 'form.submitted' in r.params:
        page.data = r.params['body']
        url = r.route_url('view_page', pagename=page.name)
        return HTTPFound(url)
    return dict(pagename=page.name, pagedata=page.data, save_url=r.route_url('edit_page', pagename=page.name))


@view_config(route_name='add_page', renderer='../templates/edit.jinja2', permission="create")
def add_page(request):
    user = request.user
    if user is None or user.role not in ('editor', 'basic'):
        raise HTTPForbidden

    pagename = request.context.pagename
    if request.dbsession.query(Page).filter_by(name=pagename).count() > 0:
        next_url = request.route_url('edit_page', pagename=pagename)
        return HTTPFound(location=next_url)
    if 'form.submitted' in request.params:
        body = request.params['body']
        page = Page(name=pagename, data=body)
        page.creator = r.user
        request.dbsession.add(page)
        next_url = request.route_url('view_page', pagename=pagename)
        return HTTPFound(location=next_url)
    save_url = request.route_url('add_page', pagename=pagename)
    return dict(pagename=pagename, pagedata='', save_url=save_url)
