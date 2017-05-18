#!/usr/bin/env python
# encoding: utf8

from setuptools import setup
import os

here = os.path.dirname(os.path.abspath(__file__))

def readme():
    "Falls back to just file().read() on any error, because the conversion to rst is only really relevant when uploading the package to pypi"
    from subprocess import CalledProcessError
    try:
        from subprocess import check_output
        return str(check_output(['pandoc', '--from', 'markdown', '--to', 'rst', os.path.join(here, 'README.md')]))
    except (ImportError, OSError, CalledProcessError) as error:
        print('python2.6 and pandoc is required to get the description as rst (as required to get nice rendering in pypi) - using the original markdown instead.',
              'See http://johnmacfarlane.net/pandoc/')
    return str(open(os.path.join(here, 'README.md')).read())

setup_args = dict(
    name='fluent',
    version='1.0.0',
    description='Python wrapper for stdlib (and other) objects to give them a fluent interface.',
    long_description=readme(),
    author='Martin Häcker',
    author_email='mhaecker@mac.com',
    license='ISC',
    url='https://github.com/dwt/fluent',
    py_modules=['fluent'],
    include_package_data=True,
    test_suite="fluent_test.py",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
)

if __name__ == '__main__':
    setup(**setup_args)
