from setuptools import setup, find_packages

setup(
    name='tripplanner',
    version="0.4",
    description="byCycle Trip Planner",
    author="Wyatt Baldwin",
    author_email="wyatt@bycycle.org",
    url="http://tripplanner.bycycle.org/",
    install_requires=["Pylons>=0.9.2",
                      "byCycle>=0.4",
                      "SQLAlchemy>=0.3"
                      ],
    packages=find_packages(),
    include_package_data=True,
    test_suite = 'nose.collector',
    package_data={'tripplanner': ['i18n/*/LC_MESSAGES/*.mo']},
    entry_points="""
    [paste.app_factory]
    main=tripplanner:make_app
    [paste.app_install]
    main=paste.script.appinstall:Installer
    """,
)
