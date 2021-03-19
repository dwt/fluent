#!/usr/bin/env python
# encoding: utf8

import setuptools
import os

here = os.path.dirname(os.path.abspath(__file__))

setup_args = dict(
    name='fluentpy',
    version='2.1',
    description='Python wrapper for stdlib (and your) objects to give them a fluent interface.',
    long_description=open(os.path.join(here, 'Readme.md')).read(),
    long_description_content_type='text/markdown',
    url='https://github.com/dwt/fluent',
    project_urls={
        'Documentation': 'https://fluentpy.readthedocs.io/',
    },
    author='Martin Häcker',
    author_email='mhaecker@mac.com',
    license='ISC',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python :: 3',
    ],
    keywords='wrapper,smalltalk,ruby,fluent,interface,functional',
    packages=setuptools.find_packages(exclude=['*.tests']),
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
            'tox',
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
    setuptools.setup(**setup_args)
