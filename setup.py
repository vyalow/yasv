import os
import re
from setuptools import setup

# -*- Classifiers -*-

classes = """
    Development Status :: 2 - Pre-Alpha
    License :: OSI Approved :: BSD License
    Intended Audience :: Developers
    Topic :: Software Development :: Libraries :: Python Modules
    Programming Language :: Python
    Programming Language :: Python :: 2
    Programming Language :: Python :: 2.7
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.2
    Programming Language :: Python :: 3.3
    Programming Language :: Python :: Implementation :: CPython
    Operating System :: OS Independent
    Operating System :: POSIX
    Operating System :: Microsoft :: Windows
    Operating System :: MacOS :: MacOS X
"""
classifiers = [s.strip() for s in classes.split('\n') if s]

# -*- Distribution Meta -*-

re_vers = re.compile(r'VERSION\s*=\s*\((.*?)\)')
rq = lambda s: s.strip("\"'")


def add_version(m):
    v = list(map(rq, m.groups()[0].split(', ')))
    return (('VERSION', '.'.join(v[0:3]) + ''.join(v[3:])), )


pats = {re_vers: add_version}

here = os.path.abspath(os.path.dirname(__file__))
meta_fh = open(os.path.join(here, 'yasv/__init__.py'))
try:
    meta = {}
    for line in meta_fh:
        if line.strip() == '# -eof meta-':
            break
        for pattern, handler in pats.items():
            m = pattern.match(line.strip())
            if m:
                meta.update(handler(m))
finally:
    meta_fh.close()

# -*- Installation Requires -*-


def strip_comments(l):
    return l.split('#', 1)[0].strip()


def reqs(*f):
    return list(filter(None, [strip_comments(l) for l in open(
        os.path.join(here, 'requirements', *f)).readlines()]))


install_requires = reqs('default.txt')

setup(
    name='yasv',
    version=meta['VERSION'],
    url='https://github.com/vyalow/yasv',
    author='Vladimir Vyalov',
    author_email='vyalov.v@gmail.com',
    description=('Yet Another Simple Validator'),
    classifiers=classifiers,
    packages=['yasv'],
    install_requires=install_requires,
)
