import gocept.httpserverlayer.wsgi
import pytest
import risclog.sqlalchemy.interfaces
import sqlalchemy
import zeit.redirect.application
import zope.component


@pytest.fixture()
def testdb(tmpdir):
    dsn = 'sqlite:///%s' % (tmpdir / 'redirect-test.db')
    engine = sqlalchemy.create_engine(dsn)
    engine.connect().execute(
        'CREATE TABLE "tmp_functest" (schema_mtime INTEGER);')
    engine.dispose()
    TestDB = type('TestDB', (object,), {'dsn': dsn})
    return TestDB()


@pytest.fixture()
def application(testdb, request):
    app = zeit.redirect.application.Application(
        **{'sqlalchemy.url': testdb.dsn,
           'testing': True})
    UNUSED_CONFIG = None
    wsgi = app(UNUSED_CONFIG)
    db = zope.component.getUtility(risclog.sqlalchemy.interfaces.IDatabase)
    request.addfinalizer(db.drop_engine)
    return wsgi


@pytest.fixture(scope='session')
def httpserver_session(request):
    server = gocept.httpserverlayer.wsgi.Layer()
    server.setUp()
    server.url = 'http://%s' % server['http_address']
    request.addfinalizer(server.tearDown)
    return server


@pytest.fixture()
def httpserver(httpserver_session, application):
    httpserver_session['httpd'].set_app(application)
    return httpserver_session
