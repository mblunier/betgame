import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'pyramid_exclog',
    'pyramid_simpleform',
    'pyramid_beaker',
    'SQLAlchemy',
    'transaction',
    'cryptacular',
    'zope.sqlalchemy',
    'waitress',
    ]

setup(name='brasil2014',
      version='0.8',
      description='brasil2014',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Markus Blunier',
      author_email='mb@rolotec.ch',
      url='http://wm2014.rolotec.ch',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='brasil2014',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = brasil2014:main
      [console_scripts]
      initialize_brasil2014_db = brasil2014.scripts.initializedb:main
      """,
      )
