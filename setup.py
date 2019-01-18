#!/usr/bin/env python
# encoding: utf8

from setuptools import setup
import os

here = os.path.dirname(os.path.abspath(__file__))

def readme():
    return open(os.path.join(here, 'Readme.md')).read()

setup_args = dict(
    name='fluentpy',
    version='1.1b3',
    description='Python wrapper for stdlib (and your) objects to give them a fluent interface.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/dwt/fluent',
    author='Martin Häcker',
    author_email='mhaecker@mac.com',
    license='ISC',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python :: 3',
    ),
    keywords='wrapper,smalltalk,ruby,fluent,interface,functional',
    py_modules=['fluentpy'],
    python_requires='>=3.6',
    include_package_data=True,
    test_suite="fluent_test.py",
    tests_require=(
        'pyexpect',
    ),
    extras_require={
        'dev': [
            'twine',
        ],
        'tests': [
            'pyexpect',
            'pytest',
        ],
        'docs': [
            'sphinx >= 1.8.3',
            'sphinx-rtd-theme >= 0.4.2',
            'autoapi >= 1.3.1',
            'recommonmark >= 0.5.0',
        ],
    },
)

if __name__ == '__main__':
    setup(**setup_args)
