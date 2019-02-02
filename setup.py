# Always prefer setuptools over distutils
# To use a consistent encoding
from codecs import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='geographica-longitude',

    version='1.0.0',

    description='Longitude',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/GeographicaGS/Longitude',

    # Author details
    author='Geographica',
    author_email='pypi@geographica.gs',

    project_urls={
        "Company": 'https://geographica.gs',
        "Source Code": "https://github.com/GeographicaGS/Longitude"
    },
    package_dir={'': 'longitude'},
    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Database',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],

    # What does your project relate to?
    keywords='carto longitude',

    packages=find_packages(where='longitude', exclude=['test*']),

    install_requires=[
        'carto==1.4.0',
        'redis==3.1.0',
        'psycopg2-binary==2.7.7'
    ],

)
