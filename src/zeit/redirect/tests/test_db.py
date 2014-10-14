from zeit.redirect.db import Redirect
import transaction


def test_create_db_object(application):
    Redirect.create(source='foo', target='bar')
    transaction.commit()
    assert 1 == Redirect.query().count()
    assert 'foo' == Redirect.query().first().source
