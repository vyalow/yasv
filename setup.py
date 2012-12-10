import os
import sys
from setuptools import setup

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import yasv


setup(
    name='yasv',
    version=yasv.__version__,
    url='https://github.com/vyalow/yasv',
    author='Vladimir Vyalov',
    author_email='vyalov.v@gmail.com',
    description=('Yet Another Simple Validator'),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=['yasv'],
)
