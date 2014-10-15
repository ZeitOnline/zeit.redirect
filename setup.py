from setuptools import setup, find_packages

setup(
    name='zeit.redirect',
    version='1.0.0.dev0',
    author='gocept',
    author_email='mail@gocept.com',
    url='https://bitbucket.org/gocept/zeit.redirect',
    description="Redirect table",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='gocept proprietary',
    namespace_packages=['zeit'],
    install_requires=[
        'gocept.logging',
        'pyramid',
        'pyramid_jinja2',
        'pyramid_tm',
        'pyramid_debugtoolbar',
        'repoze.vhm',
        'risclog.sqlalchemy >= 1.7.1.dev0',
        'setuptools',
        'zope.component',
        'zope.configuration',
        'zope.event',
        'zope.interface',
    ],
    extras_require={
        'test': [
            'gocept.httpserverlayer',
            'requests',
            'risclog.sqlalchemy [test]',
    ]},
    entry_points={
        'paste.app_factory': [
            'application = zeit.redirect.application:paste_app_factory',
        ],
        'console_scripts': [
            'initialize_db = zeit.redirect.db:initialize_db',
        ],
    },
)
