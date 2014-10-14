from pyramid.paster import setup_logging, get_appsettings
from pyramid.view import view_config
import json
import logging
import pkg_resources
import pyramid.config
import pyramid.registry
import pyramid_jinja2
import risclog.sqlalchemy.db
import risclog.sqlalchemy.serializer
import transaction
import zeit.redirect
import zope.component
import zope.configuration.config
import zope.configuration.xmlconfig


log = logging.getLogger(__name__)


class IApplication(zope.interface.Interface):
    pass


class Application(object):

    zope.interface.implements(IApplication)

    DONT_SCAN = ['.testing', '.tests', '.conftest']

    @classmethod
    def from_filename(cls, filename, **kw):
        """Creates an application from a paste.ini file."""
        setup_logging(filename)
        settings = get_appsettings(filename)
        settings.update(kw)
        app = cls(**settings)
        UNUSED_CONFIG = None
        return app(UNUSED_CONFIG)

    def __init__(self, **settings):
        self.settings = settings

    def __call__(self, global_config, **settings):
        self.settings.update(settings)
        zope.component.provideUtility(self)
        self.configure()
        return self.make_wsgi_app(global_config)

    def configure(self):
        self.configure_zca()
        self.configure_db()
        self.configure_pyramid()

    def configure_zca(self):
        return  # XXX unneeded?
        # log.debug('Configuring ZCA')
        # context = zope.configuration.config.ConfigurationMachine()
        # zope.configuration.xmlconfig.registerCommonDirectives(context)
        # filename = ('application.zcml' if not self.settings.get('testing')
        #             else 'testing.zcml')
        # zope.configuration.xmlconfig.include(
        #     context, package=zeit.redirect, file=filename)
        # context.execute_actions()
        # return context

    def configure_db(self):
        self.configure_sqlalchemy_models()
        dsn = self.settings['sqlalchemy.url']
        log.debug('Configuring database %s', dsn)
        testing = bool(self.settings.get('testing'))
        db = risclog.sqlalchemy.db.get_database(
            testing=testing)
        db.register_engine(dsn)
        if testing:
            db.create_all()
            transaction.commit()
        try:
            # Edge case for initialize_db
            if self.settings.get('check_db_revision', True):
                db.assert_database_revision_is_current()
        except ValueError:
            raise SystemExit(
                "Database revision does not match current head. "
                "Please run batou to get migrated to the latest revision.")

    def configure_sqlalchemy_models(self):
        # XXX Use a scanning mechanism instead of explicitly listing modules.
        for module in ['db']:
            module = __import__(
                module, globals(), locals(), fromlist=None, level=1)

    def configure_pyramid(self):
        log.debug('Configuring Pyramid')

        self.settings['jinja2.filters'] = dict(
            tojson=json.dumps,
        )

        registry = pyramid.registry.Registry(
            bases=(zope.component.getGlobalSiteManager(),))
        self.config = config = pyramid.config.Configurator(
            settings=self.settings,
            registry=registry)
        config.setup_registry(settings=self.settings)

        config.include('pyramid_tm')
        config.include('pyramid_debugtoolbar')
        config.include('pyramid_jinja2')
        config.add_renderer('.html', pyramid_jinja2.renderer_factory)

        config.add_static_view(
            'resources', 'zeit.redirect:resources', cache_max_age=3600)

        config.add_renderer(
            'json', risclog.sqlalchemy.serializer.json_renderer_factory())

        self.configure_routes()

        config.scan(package=zeit.redirect, ignore=self.DONT_SCAN)
        return config

    def configure_routes(self):
        c = self.config
        c.add_route('ping', '/_ping')
        c.add_route('add', '/_add')
        c.add_route('redirect', '/*path')

    @property
    def pipeline(self):
        """Configuration of a WSGI pipeline.

        Our WSGI application is wrapped in each filter in turn,
        so the first entry in this list is closest to the application,
        and the last entry is closest to the WSGI server.

        Each entry is a tuple (spec, protocol, name, arguments).
        The default meaning is to load an entry point called ``name`` of type
        ``protocol`` from the package ``spec`` and load it, passing
        ``arguments`` as kw parameters (thus, arguments must be a dict).

        If ``protocol`` is 'factory', then instead of an entry point the method
        of this object with the name ``spec`` is called, passing ``arguments``
        as kw parameters.

        """
        return [
            ('repoze.vhm', 'paste.filter_app_factory', 'vhm_xheaders', {}),
        ]

    def make_wsgi_app(self, global_config):
        app = self.config.make_wsgi_app()
        for spec, protocol, name, extra in self.pipeline:
            if protocol == 'factory':
                factory = getattr(self, spec)
                app = factory(app, **extra)
                continue
            entrypoint = pkg_resources.get_entry_info(spec, protocol, name)
            app = entrypoint.load()(app, global_config, **extra)
        return app

paste_app_factory = Application().__call__


@view_config(route_name='ping', renderer='string')
def ping(request):
    return 'ping'
