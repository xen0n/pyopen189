#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re
import ast

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def extract_version():
    with open('pyopen189/__init__.py', 'rb') as f_version:
        ast_tree = re.search(
            r'__version__ = (.*)',
            f_version.read().decode('utf-8')
        ).group(1)
        if ast_tree is None:
            raise RuntimeError('Cannot find version information')
        return str(ast.literal_eval(ast_tree))


with open('README.rst', 'rb') as f_readme:
    readme = f_readme.read().decode('utf-8')

packages = [str('pyopen189')]

version = extract_version()

setup(
    name='pyopen189',
    version=version,
    keywords=['189', 'tianyi', 'sdk', 'client'],
    description='Unofficial Python client for open.189.cn',
    long_description=readme,
    author='xen0n',
    author_email='idontknw.wang@gmail.com',
    license='BSD',
    url='https://github.com/xen0n/pyopen189',
    download_url='https://github.com/xen0n/pyopen189',

    install_requires=[
        'pytz',
        'requests',
        'six',
    ],
    packages=packages,

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
