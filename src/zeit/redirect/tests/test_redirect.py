from zeit.redirect.db import Redirect
import requests
import transaction


def test_no_redirect_returns_200(httpserver):
    r = requests.get(httpserver.url + '/foo')
    assert 200 == r.status_code


def test_redirect_returns_301(httpserver):
    Redirect.create(source='/foo', target='/bar')
    transaction.commit()
    r = requests.get(httpserver.url + '/foo', allow_redirects=False)
    assert 301 == r.status_code
    assert httpserver.url + '/bar' == r.headers['Location']
