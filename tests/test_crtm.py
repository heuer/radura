# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 - 2014 -- Lars Heuer - Semagia <http://www.semagia.com/>.
# All rights reserved.
#
# BSD license.
#
"""\
Tests against the CRTM lexer.

:author:       Lars Heuer (heuer[at]semagia.com)
:organization: Semagia - http://www.semagia.com/
:license:      BSD license
"""
from nose.tools import eq_, ok_
from pygments.token import *
from radura.tm import CRTMLexer


def lex(s):
    lexer = CRTMLexer()
    return list(lexer.get_tokens(s))


_WS = (Text, u' ')
_COLON = (Punctuation, u':')


def test_lang2scope_directive():
    data = [(u'%langtoscope true', [(Keyword, u'%langtoscope'), _WS, (Keyword, u'true')]),
            (u'%langtoscope false', [(Keyword, u'%langtoscope'), _WS, (Keyword, u'false')])]
    for txt, tokens in data:
        wanted = tokens[:]
        wanted.append((Text, u'\n'))
        yield eq_, wanted, lex(txt)


def test_context_sensitive_keywords():
    data = [(u'ako: ako', [(Name, u'ako'), _COLON, _WS, (Keyword, u'ako')]),
            (u'lang true false', [(Name, u'lang'), _WS, (Name, u'true'), _WS, (Name, u'false')]),
            (u'x: -; lang= true y: -', [(Name, u'x'), _COLON, _WS, (Keyword, u'-'),
                                        (Punctuation, u';'), _WS, (Keyword, u'lang'), (Punctuation, u'='), _WS, (Keyword, u'true'),
                                        _WS, (Name, u'y'), _COLON, _WS, (Keyword, u'-')])]
    for txt, tokens in data:
        wanted = tokens[:]
        wanted.append((Text, u'\n'))
        yield eq_, wanted, lex(txt)


def test_scope():
    data = [(u'x: @theme1', [(Name, u'x'),_COLON, _WS, (Punctuation, u'@'), (Name, u'theme1')]),
            (u'x: @theme1, theme2', [(Name, u'x'), _COLON, _WS, (Punctuation, u'@'), (Name, u'theme1'), (Punctuation, u','), _WS, (Name, u'theme2')])]
    for txt, tokens in data:
        wanted = tokens[:]
        wanted.append((Text, u'\n'))
        yield eq_, wanted, lex(txt)


def test_occ_no_kw():
    data = [(u'foaf:homepage: <http://psi.example.org/homepage> x: -',
             [(Name, u'foaf:homepage'), _COLON, _WS, (Literal, u'<http://psi.example.org/homepage>'), _WS,
              (Name, u'x'), _COLON, _WS, (Keyword, u'-')])]
    for txt, tokens in data:
        wanted = tokens[:]
        wanted.append((Text, u'\n'))
        yield eq_, wanted, lex(txt)


def test_accept():
    def no_error(tokens):
        ok_(Error not in tokens)
    data = (u'%include <foaf.crtm>', u'''%prefix foaf <http://xmlns.com/foaf/0.1/>

foaf {
  name: name
  nick: name
}''', u'''%prefix doap <http://usefulinc.com/ns/doap#>
%prefix foaf <http://xmlns.com/foaf/0.1/>

doap {
  shortdesc, description: occurrence
}

foaf {
  name: name
  nick: name
}''', u'''#
# CRTM example that maps a subset of the DOAP voc. to Topic Maps
#
%prefix doap <http://usefulinc.com/ns/doap#>
%prefix tmdm <http://psi.topicmaps.org/iso13250/model/>
%prefix rdf <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
%prefix foaf <http://xmlns.com/foaf/0.1/>
%prefix ex <http://psi.example.org/doap/>

rdf:type: isa

foaf {
  # Map the foaf:name type to the default name type.
  name: - tmdm:topic-name
  homepage: occurrence
}

doap {
  # Map the doap:name type to the default name type.
  name: - tmdm:topic-name

  shortname: name

  # Map all of the following DOAP properties to occurrences
  shortdesc, description,
  homepage, download-page,
  bug-database, mailing-list,
  license, programming-language, browse: occurrence

  # Create an association from the repository property
  repository: ex:has-repository(ex:project, ex:repository)

  # Create an assoc from the maintainer property
  maintainer: ex:maintains(ex:project, ex:maintainer)

  # Treat the repository URL as subject locator.
  location: subject-locator
}
''',
u'''
%prefix doap <http://usefulinc.com/ns/doap#>
doap {
    123: name
}
'''
)
    for d in data:
        tokens = [t[0] for t in lex(d)]
        yield no_error, tokens


if __name__ == '__main__':
    import nose
    nose.core.runmodule()
