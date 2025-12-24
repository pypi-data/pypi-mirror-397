# -*- config:utf-8 -*-

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from codecs import open
from os import path
import re

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'src/__version__.py'), encoding='utf-8') as fp:
    try:
        version = re.findall(
            r"^__version__ = \"([^']+)\"\r?$", fp.read(), re.M
        )[0]
    except IndexError:
        raise RuntimeError("Unable to determine version.")

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='syncdb',
    version=version,
    license='MIT',
    description='Live synchronization engine to push database changes to multiple targets in real-time.',
    long_description_content_type='text/markdown',
    long_description=long_description,
    url='https://github.com/getfernand/syncdb',
    author='Cyril Nicodeme',
    author_email='contact@cnicodeme.com',
    keywords='live sync database synchronization engine',
    project_urls={
        # 'Official Website': 'https://github.com/getfernand/syncdb',
        # 'Documentation': 'https://github.com/getfernand/syncdb',
        'Source': 'https://github.com/getfernand/syncdb',
    },
    packages=find_packages(),
    install_requires=[
        'SQLAlchemy>=2.0.20'
    ],
    extras_require={
        'dev': ['pytest>=8.3.4'],
    },
    python_requires='>=3.10, <4',
    platforms='any',

    # For a list of valid classifiers, see
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',

        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',

        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: System :: Networking",

        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Environment :: Web Environment",

        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: 3.15",
        "Programming Language :: Python :: Implementation :: PyPy",
    ]
)
