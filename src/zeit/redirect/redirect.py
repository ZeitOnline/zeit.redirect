from pyramid.httpexceptions import HTTPMovedPermanently
from pyramid.view import view_config
from zeit.redirect.db import Redirect
import json


@view_config(route_name='redirect', renderer='string')
def check_redirect(request):
    redirect = Redirect.query().filter_by(source=request.path).first()
    if redirect:
        # XXX Should we be protocol-relative (https etc.)?
        raise HTTPMovedPermanently(
            'http://' + request.headers['Host'] + redirect.target)
    else:
        return ''


@view_config(route_name='add', renderer='string', request_method='POST')
def add_redirect(request):
    body = json.loads(request.body)
    redirect = Redirect.find_or_create(source=body['source'])
    redirect.target = body['target']
    return '{}'
