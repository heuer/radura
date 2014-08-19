# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 - 2014 -- Lars Heuer - Semagia <http://www.semagia.com/>.
# All rights reserved.
#
# BSD license.
#
"""\
Setup script.
"""
from setuptools import setup, find_packages

setup(
      name = 'radura',
      version = '0.0.1',
      description = 'Pygments lexers for Topic Maps syntaxes',
      long_description = '\n\n'.join([open('README.txt').read(), open('CHANGES.txt').read()]),
      author = 'Lars Heuer',
      author_email = 'mappa@googlegroups.com',
      url = 'http://mappa.semagia.com/',
      license = 'BSD',
      packages = find_packages(),
      entry_points = """
      [pygments.lexers]
      ctm = radura.tm:CTMLexer
      tolog = radura.tm:TologLexer
      crtm = radura.tm:CRTMLexer
      """,
      platforms = 'any',
      zip_safe = False,
      include_package_data = True,
      package_data = {'': ['*.txt']},
      install_requires=['pygments'],
      keywords = ['Topic Maps', 'syntax highlighting'],
      classifiers = [
                    'Intended Audience :: Developers',
                    'Intended Audience :: Information Technology',
                    'Topic :: Software Development',
                    'Topic :: Software Development :: Libraries',
                    'Topic :: Software Development :: Libraries :: Python Modules',
                    'License :: OSI Approved :: BSD License',
                    'Operating System :: OS Independent',
                    'Programming Language :: Python',
                    ]
      )
