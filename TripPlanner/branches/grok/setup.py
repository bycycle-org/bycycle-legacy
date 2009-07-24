from setuptools import setup, find_packages


setup(
    name='bycycle.tripplanner',
    version='0.5',
    description='',
    long_description='',
    # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[], 
    keywords='',
    author='',
    author_email='',
    url='',
    license='',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'bycycle.core==dev,>=0.5dev',
        'setuptools',
        'grok',
        'grokui.admin',
        'grokcore.startup',
        'z3c.testsetup',
    ],
    entry_points = """
    [console_scripts]
    bycycletripplanner-debug = grokcore.startup:interactive_debug_prompt
    bycycletripplanner-ctl = grokcore.startup:zdaemon_controller

    [paste.app_factory]
    main = grokcore.startup:application_factory
    """,
)
