#!/usr/bin/env python

from setuptools import setup, find_packages
import os
import viewpoint

try:
    long_desc = open(os.path.join(os.path.dirname(__file__), 'README')).read()
except (IOError, OSError):
    long_desc = ''

try:
    reqs = open(os.path.join(os.path.dirname(__file__), 'requirements.txt')).read()
except (IOError, OSError):
    reqs = ''

version = viewpoint.get_version()

setup(
    name = 'viewpoint',
    version = version,
    description = 'A simple blog with hooks for categories, tinymce, tags and other things',
    long_description = long_desc,
    author = 'Justin Quick, Corey Oordt',
    author_email = 'jquick@washingtontimes.com, coordt@washingtontimes.com',
    url = 'http://opensource.washingtontimes.com/projects/viewpoint/',
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
    ],
    packages = find_packages(),
    include_package_data=True,
    install_requires = reqs,
    dependency_links = [
        'http://opensource.washingtontimes.com/static/dist/django-categories-0.2.1.tar.gz#md5=692714a07a18493c45e575cd26b07b09'
    ]
)
