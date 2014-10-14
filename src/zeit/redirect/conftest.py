import pytest
import sqlalchemy
import zeit.redirect.application


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
def application(testdb):
    app = zeit.redirect.application.Application(
        **{'sqlalchemy.url': testdb.dsn,
           'testing': True})
    UNUSED_CONFIG = None
    return app(UNUSED_CONFIG)
