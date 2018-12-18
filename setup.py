#!/usr/bin/env python

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='nifty-nesting',
      version='0.2.3',
      description='Python utilities for arbitrarily nested data structures.',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Aetius Flavius',
      author_email='aetius.flavius.390@gmail.com',
      url='https://github.com/aetiusflavius/nifty-nesting/',
      packages=['nifty_nesting'],
      install_requires=['attrs', 'six'],
      keywords=['nested', 'data', 'structure', 'arbitrary', 'utilities', 'manipulation'],
      classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3'
      ]
     )
