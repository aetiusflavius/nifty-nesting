from distutils.core import setup

setup(
    name='Nifty-Nesting',
    version='0.1',
    packages=['nifty_nesting',],
    install_requires=[
          'attrs',
          'six'
    ],
    license='MIT License',
    long_description=open('README.md').read(),
)
