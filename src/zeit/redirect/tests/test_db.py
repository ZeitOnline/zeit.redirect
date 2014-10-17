from zeit.redirect.db import Redirect
import transaction


def test_create_db_object(application):
    Redirect.create(source='foo', target='bar')
    transaction.commit()
    assert 1 == Redirect.query().count()
    assert 'foo' == Redirect.query().first().source


def test_chained_redirects_all_point_to_the_latest_target(application):
    Redirect.add('a', 'b')
    Redirect.add('b', 'c')
    transaction.commit()
    assert 'c' == Redirect.query().filter_by(source='a').first().target
    assert 'c' == Redirect.query().filter_by(source='b').first().target


def test_inverse_redirect_does_not_create_cycle(application):
    Redirect.add('a', 'b')
    Redirect.add('b', 'a')
    transaction.commit()
    assert 1 == Redirect.query().count()
    assert 'a' == Redirect.query().filter_by(source='b').first().target
