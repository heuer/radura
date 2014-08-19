# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 - 2014 -- Lars Heuer - Semagia <http://www.semagia.com/>.
# All rights reserved.
#
# BSD license.
#
"""\
Lexers for Topic Maps syntaxes.

:author:       Lars Heuer (heuer[at]semagia.com)
:organization: Semagia - http://www.semagia.com/
:license:      BSD license
"""
import sys
import re
from pygments.lexer import RegexLexer, include, bygroups, using
from pygments.token import Punctuation, Literal, Text, Comment, Operator, Keyword, Name, String, Number
from radura.tokens import IRI, QName, Wildcard

__all__ = ['CTMLexer', 'TologLexer', 'CRTMLexer']

# Start of an identifier
_IDENT_START = ur'[a-zA-Z_]' \
               ur'|[\u00C0-\u00D6]|[\u00D8-\u00F6]' \
               ur'|[\u00F8-\u02FF]|[\u0370-\u037D]' \
               ur'|[\u037F-\u1FFF]|[\u200C-\u200D]' \
               ur'|[\u2070-\u218F]|[\u2C00-\u2FEF]' \
               ur'|[\u3001-\uD7FF]|[\uF900-\uFDCF]' \
               ur'|[\uFDF0-\uFFFD]'

if not sys.maxunicode == 0xffff:
    # <http://bugs.python.org/issue12729>, <http://bugs.python.org/issue12749>,
    # <http://bugs.python.org/issue3665>
    _IDENT_START += ur'|[\U00010000-\U000EFFFF]'
del sys

_IDENT_PART = ur'%s|[\-0-9]|[\u00B7]|[\u0300-\u036F]|[\u203F-\u2040]' % _IDENT_START

# Identifier
_IDENT = ur'(%s)+(\.*(%s))*' % (_IDENT_START, _IDENT_PART)

# QNames
_QNAME = ur'%s:(?:(?:[0-9]+(?:%s)*)|%s)' % (_IDENT, _IDENT_PART, _IDENT)
_CURIE = ur'\[%s:[^<>\"\{\}\`\\\] ]+\]' % _IDENT

_DATE = ur'\-?(000[1-9]|00[1-9][0-9]|0[1-9][0-9][0-9]|[1-9][0-9][0-9][0-9]+)\-(0[1-9]|1[0-2])\-(0[1-9]|1[0-9]|2[0-9]|3[0-1])'
_TZ = ur'Z|((\+|\-)[0-9]{2}:[0-9]{2})'
_TIME = r'[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?(%s)?' % _TZ

_IRI = ur'<[^<>\"\{\}\`\\ ]+>'


class CTMLexer(RegexLexer):
    """\
    `Compact Topic Maps Syntax (CTM) <http://www.isotopicmaps.org/ctm/>`_ lexer.
    """
    name = u'CTM'
    aliases = [u'ctm']
    filenames = [u'*.ctm', u'*.tmcl']
    mimetypes = [u'application/x-tm+ctm']
    
    flags = re.UNICODE

    tokens = {
            'root': [
                (ur'\s+', Text),
                (ur'(def)(\s+)(%s)' % _IDENT, bygroups(Keyword, Text, Name.Function)),
                include('iris'),
                (ur'(end|isa|ako)\b', Keyword),
                (ur'(%%prefix)(\s+)(%s)(\s+)([^\s]+)' % _IDENT, bygroups(Keyword, Text, Name.Namespace, Text, IRI)),
                (ur'(%encoding|%version|%include|%mergemap)\b', Keyword),
                (ur'\*', Keyword.Constant),
                (ur'"{3}([^"\\]|(\\[\\"rntuU])|"|"")*"{3}', String),
                (ur'"([^"\\]|(\\[\\"rntuU]))*"', String),
                (ur'\?%s' % _IDENT, Wildcard),
                (ur'\?', Wildcard),
                (ur'\$%s' % _IDENT, Name.Variable),
                (ur'%sT%s' % (_DATE, _TIME), Literal.Date),
                (_DATE, Literal.Date),
                (ur'(\-|\+)?([0-9]+\.[0-9]+|\.([0-9])+)', Number.Float),
                (ur'(\-|\+)?[0-9]+', Number.Integer),
                (ur'(%s)(\s*)(\()(?!.+?:)' % _IDENT, bygroups(Name.Function, Text, Punctuation)),
                (_QNAME, QName),
                (_IDENT, Name),
                (ur'#\(', Comment.Multiline, 'multiline-comments'),
                (ur'#[^\n]*', Comment.Single),
                (ur'[\[\]\(\),;\-\.=\^@:]+', Punctuation),
            ],
            'multiline-comments': [
                (ur'\)#', Comment.Multiline, '#pop'),
                (ur'#\(', Comment.Multiline, '#push'),
                (ur'[^#\(\)]+', Comment.Multiline),
                (ur'#|\(|\)', Comment.Multiline),
            ],
            'iris': [
                (_IRI, IRI),
                (ur'[a-zA-Z]+[a-zA-Z0-9\+\-\.]*://([;\.\)]*[^\s;\]\.\(\)]+)+', IRI),
            ],
        }


class TologLexer(RegexLexer):
    """\
    tolog Topic Maps query language lexer. 
    
    Supports tolog+ as well.
    """
    name = u'tolog'
    aliases = [u'Tolog']
    filenames = [u'*.tl', u'*.tolog']
    mimetypes = [u'application/x-tolog']

    flags = re.UNICODE

    tokens = {
            'root': [
                (ur'\s+', Text),
                (ur'#[^\n]*', Comment.Single),
                (ur'/\*', Comment.Multiline, 'multiline-comments'),
                include('builtins'),
                (ur'(?i)(select|delete|update|from|merge|order|by|asc|desc|count|not)\b', Keyword),
                (ur'(?i)(create|load|drop|into|where)\b', Keyword),  # t+
                (ur'(?i)(import)(\s+)("(?:[^"]|"{2})*")(\s+)(as)(\s+)(%s)' % _IDENT, bygroups(Keyword, Text, IRI, Text, Keyword, Text, Name.Namespace)),
                (ur'(?i)(using)(\s+)(%s)(\s+)(for)(\s+)([ias]"(?:[^"]|"{2})*")' % _IDENT, bygroups(Keyword, Text, Name.Namespace, Text, Keyword, Text, IRI)),
                (ur'(%%prefix|%%import)(\s+)(%s)(\s+)([^\s]+)' % _IDENT, bygroups(Keyword, Text, Name.Namespace, Text, IRI)),
                (ur'(%version|%base|%x-[^\s]+)\b', Keyword),
                (ur'(?i)insert\b', Keyword, 'insert'),
                (ur'[ias]"(?:[^"]|"{2})*"', IRI),
                (ur'"([^"]|"{2})*"', String),
                (ur'@([0-9]+|[0-9]*%s)' % _IDENT, Name.Variable.Instance),
                (ur'\$%s' % _IDENT, Name.Variable),
                (ur'%%%s%%' % _IDENT, Name.Variable),
                (ur'%sT%s' % (_DATE, _TIME), Literal.Date),
                (_DATE, Literal.Date),
                (ur'(\-|\+)?([0-9]+\.[0-9]+|\.([0-9])+)', Number.Float),
                (ur'(\-|\+)?[0-9]+', Number.Integer),
                (ur'(%s)(\s*)(\()(?=.+?:\-)' % _IDENT, bygroups(Name.Function, Text, Punctuation)),
                (ur'((?:%s)|(?:%s)|(?:%s))(\s*)(\()(?!.+?:\s+)' % (_IDENT, _QNAME, _CURIE), bygroups(Name.Function, Text, Punctuation)),
                (_CURIE, QName),
                (_QNAME, QName),
                (_IDENT, Name),
                (_IRI, IRI),
                (ur'[\(\),{}\|\.\^:\-\?]+', Punctuation),
                (ur'/?=|<=?|>=?', Operator),
            ],
            'builtins': [
                (ur'\b(association|association-role|base-locator'
                 ur'|datatype|direct-instance-of|instance-of|item-identifier'
                 ur'|object-id|occurrence|reifies|resource|role-player'
                 ur'|scope|source-locator|subject-identifier|subject-locator'
                 ur'|topic|topicmap|topic-name|type|value|value-like|variant)(\s*)(\()', bygroups(Name.Builtin, Text, Punctuation)),
            ],
            'insert': [
                (ur'(?is)(.+?)(\b(?:into|from|where)\b)', bygroups(using(CTMLexer), Keyword), '#pop'),
            ],
            'multiline-comments': [
                (ur'/\*', Comment.Multiline, '#push'),
                (ur'\*/', Comment.Multiline, '#pop'),
                (ur'[^/\*]+', Comment.Multiline),
                (ur'[/*]', Comment.Multiline)
            ],
        }


class CRTMLexer(RegexLexer):
    """\
    `Compact RDF to Topic Maps (CRTM) <http://www.semagia.com/tr/crtm/>`_ lexer.
    """
    name = u'CRTM'
    aliases = [u'crtm']
    filenames = [u'*.crtm']
    mimetypes = [u'application/x-tm+crtm']

    flags = re.UNICODE

    tokens = {
        'root': [
                (ur'\s+', Text),
                (ur'#[^\n]*', Comment.Single),
                (ur'(%%prefix)(\s+)(%s)(\s+)([^\s]+)' % _IDENT, bygroups(Keyword, Text, Name.Namespace, Text, IRI)),
                (ur'(%langtoscope)(\s+)(true|false)', bygroups(Keyword, Text, Keyword)),
                (ur'(%include)\b', Keyword),
                (_IRI, IRI),
                (_QNAME, QName),
                (ur'%s|([0-9]+(\.*%s)*)' % (_IDENT, _IDENT_PART), Name),
                (ur'[:;]', Punctuation, 'rhs'),
                (ur'[=\(\),{}@]+', Punctuation),
        ],
        'rhs': [
                (ur'\s+', Text),
                (ur'lang', Keyword),
                (ur'(association|assoc|occurrence|occ|name|-|isa|ako'
                 ur'|item-identifier|iid'
                 ur'|subject-identifier|sid'
                 ur'|subject-locator|slo'
                 ur'|true|false)', Keyword, '#pop'),
                (_IRI, IRI, '#pop'),
                (_QNAME, QName, '#pop'),
                (ur'%s|([0-9]+(\.*%s)*)' % (_IDENT, _IDENT_PART), Name, '#pop'),
                (ur'[=]', Punctuation),
                (ur'[\(\)@]', Punctuation, '#pop'),
        ],
    }
