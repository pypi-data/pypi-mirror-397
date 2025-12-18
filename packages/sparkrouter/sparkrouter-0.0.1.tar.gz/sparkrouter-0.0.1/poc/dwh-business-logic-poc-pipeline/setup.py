#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import io
# import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup

packages=find_packages('src')
package_data = {pkg: ['*.sql'] for pkg in packages}

def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()

# Read version from VERSION file
with open('VERSION') as f:
    version = f.read().strip()


setup(
    name='dwh-pipeline-poc',
    version=version,
    license='BSD',
    description='DWH BusinessLogic POC',
    # long_description='to-do-long-description',
    # long_description='%s\n%s' % (
    #     re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub('', read('README.rst')),
    #     re.sutoxb(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
    # ),
    author='Shutterfly Data Warehouse',
    author_email='jclark@shutterfly.com',
    url='https://github.com/sflyinc-jclark/dwh-business-logic-poc-pipeline',
    packages=packages,
    package_dir={'': 'src'},
    include_package_data=True,
    package_data=package_data,
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        # uncomment if you test on these interpreters:
        # 'Programming Language :: Python :: Implementation :: IronPython',
        # 'Programming Language :: Python :: Implementation :: Jython',
        # 'Programming Language :: Python :: Implementation :: Stackless',
        'Topic :: Utilities',
    ],
    # keywords=[
    #     # eg: 'keyword1', 'keyword2', 'keyword3',
    # ],
    # install_requires=[
    #     'psycopg2-binary==2.9.10',
    #     'pytz==2025.2',
    #     'python-dateutil==2.9.0.post0',
    #     'pandas==2.3.0'
    # ],
    # extras_require={
    #     # eg:
    #     #   'rst': ['docutils>=0.11'],
    #     #   ':python_version=="2.6"': ['argparse'],
    # },
    # entry_points={
    #     'console_scripts': [
    #         'dwh = dwh.cli:main',
    #     ]
    # },
)