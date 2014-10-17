from sqlalchemy import Column, Integer, String
import gocept.logging
import risclog.sqlalchemy.db
import risclog.sqlalchemy.model
import sqlalchemy.exc
import transaction


class ObjectBase(risclog.sqlalchemy.model.ObjectBase):

    id = Column(Integer, primary_key=True)


Object = risclog.sqlalchemy.model.declarative_base(
    ObjectBase, class_registry=risclog.sqlalchemy.model.class_registry)


class Redirect(Object):

    source = Column(String, unique=True)
    target = Column(String)

    @classmethod
    def add(cls, source, target):
        redirect = cls.find_or_create(source=source)
        redirect.target = target


def initialize_db():
    parser = gocept.logging.ArgumentParser(
        description=u'Initialize database schema.')
    parser.add_argument(
        '-c', '--config', default='paste.ini#redirect',
        help='Specify the config file. (default: paste.ini#redirect)')
    parser.add_argument(
        '-f', '--force', action='store_true',
        help='Force update if database already exists.')
    args = parser.parse_args()

    import zeit.redirect.application
    zeit.redirect.application.Application.from_filename(
        args.config, check_db_revision=False)
    db = risclog.sqlalchemy.db.get_database()
    if args.force:
        db.empty()
    else:
        try:
            with transaction.manager:
                Redirect.query().all()
        except sqlalchemy.exc.DatabaseError:
            pass
    db.create_all()
