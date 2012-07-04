# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 -- Lars Heuer - Semagia <http://www.semagia.com/>.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
#     * Neither the name of the project nor the names of the contributors 
#       may be used to endorse or promote products derived from this 
#       software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
"""\
Lexers for Topic Maps syntaxes.
"""
import re
from pygments.lexer import RegexLexer, include, bygroups
from pygments.token import Punctuation, Literal, Text, Comment, Operator, Keyword, Name, String, Number
from radura.tokens import IRI, QName, Wildcard

__all__ = ['CTMLexer', 'TologLexer']

# Start of an identifier
_ident_start = ur'[a-zA-Z_]|[\u00C0-\u00D6]|[\u00D8-\u00F6]' + \
                ur'|[\u00F8-\u02FF]|[\u0370-\u037D]' + \
                ur'|[\u037F-\u1FFF]|[\u200C-\u200D]' + \
                ur'|[\u2070-\u218F]|[\u2C00-\u2FEF]' + \
                ur'|[\u3001-\uD7FF]|[\uF900-\uFDCF]|[\uFDF0-\uFFFD]'

_ident_part = ur'%s|[\-0-9]|[\u00B7]|[\u0300-\u036F]|[\u203F-\u2040]' % _ident_start

# Identifier
_ident = ur'(?:%s)+(?:\.*(?:%s))*' % (_ident_start, _ident_part)

# QNames
_qname = ur'%s:(?:(?:[0-9]+(?:%s)*)|%s)' % (_ident, _ident_part, _ident)

_date = r'\-?(000[1-9]|00[1-9][0-9]|0[1-9][0-9][0-9]|[1-9][0-9][0-9][0-9]+)\-(0[1-9]|1[0-2])\-(0[1-9]|1[0-9]|2[0-9]|3[0-1])'
# Timezone
_tz = r'Z|((\+|\-)[0-9]{2}:[0-9]{2})'
# Time
_time = r'[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?(%s)?' % _tz


class CTMLexer(RegexLexer):
    """\
    `Compact Topic Maps Syntax (CTM) <http://www.isotopicmaps.org/ctm/>`_ lexer.
    """
    name = 'CTM'
    aliases = ['ctm']
    filenames = ['*.ctm', '*.tmcl']
    mimetypes = ['application/x-tm+ctm']
    
    flags = re.UNICODE

    tokens = {
            'root': [
                (r'\s+', Text),
                (r'(def)(\s+)', bygroups(Keyword, Text), 'template'),
                include('iris'),
                (r'(end|isa|ako)\b', Keyword),
                (r'(%%prefix)(\s+)(%s)(\s+)([^\s]+)' % _ident, bygroups(Keyword, Text, Name.Namespace, Text, IRI)),
                (r'(%encoding|%version|%include|%mergemap)\b', Keyword),
                (r'\*', Keyword.Constant),
                (r'"{3}([^"\\]|(\\[\\"rntuU])|"|"")*"{3}', String),
                (r'"([^"\\]|(\\[\\"rntuU]))*"', String),
                (ur'\?%s' % _ident, Wildcard),
                (r'\?', Wildcard),
                (ur'\$%s' % _ident, Name.Variable),
                (r'%sT%s' % (_date, _time), Literal.Date),
                (_date, Literal.Date),
                (r'(\-|\+)?([0-9]+\.[0-9]+|\.([0-9])+)', Number.Float),
                (r'(\-|\+)?[0-9]+', Number.Integer),
                (ur'(%s)(\s*)(\()(?!.+?:)' % _ident, bygroups(Name.Function, Text, Punctuation)), 
                (_qname, QName),
                (_ident, Name),
                (r'#\(', Comment.Multiline, 'multiline-comments'),
                (r'#[^\n]*', Comment.Single),
                (r'[\[\]\(\),;\-\.=\^@:]+', Punctuation),
            ],
            'template': [
                (_ident, Name.Function, '#pop'),
            ],
            'multiline-comments': [
                (r'\)#', Comment.Multiline, '#pop'),
                (r'#\(', Comment.Multiline, '#push'),
                (r'[^#\(\)]+', Comment.Multiline),
                (r'#|\(|\)', Comment.Multiline),
            ],
            'iris': [
                (r'<[^<>\"\{\}\`\\ ]+>', IRI),
                (r'[a-zA-Z]+[a-zA-Z0-9\+\-\.]*://([;\.\)]*[^\s;\]\.\(\)]+)+', IRI),
            ],
        }



class TologLexer(RegexLexer):
    """\
    tolog Topic Maps query language lexer. 
    
    Supports tolog+ as well.
    """
    name = 'tolog'
    aliases = ['Tolog']
    filenames = ['*.tl', '*.tolog']
    mimetypes = ['application/x-tolog']

    flags = re.UNICODE

    tokens = {
            'root': [
                (r'\s+', Text),
                (r'#[^\n]*', Comment.Single),
                (r'/\*', Comment.Multiline, 'multiline-comments'),
                include('builtins'),
                (r'(?i)(select|insert|delete|update|from|merge|order|by|asc|desc)\b', Name.Keyword),
                (r'(?i)(create|load|drop|into|where)\b', Name.Keyword), #t+
                (r'(?i)(import)(\s+)("(?:[^"]|"{2})*")(\s+)(as)(\s+)(%s)' % _ident, bygroups(Keyword, Text, IRI, Text, Keyword, Text, Name.Namespace)),
                (r'(?i)(using)(\s+)(%s)(\s+)(for)(\s+)([ias]"(?:[^"]|"{2})*")' % _ident, bygroups(Keyword, Text, Name.Namespace, Text, Keyword, Text, IRI)),
                (r'(%%prefix|%%import)(\s+)(%s)(\s+)([^\s]+)' % _ident, bygroups(Keyword, Text, Name.Namespace, Text, IRI)),
                (r'\b(%version|%base|%x-[^\s]+)\b', Keyword),
                (r'"([^"]|"{2})*"', String),
                (ur'\$%s' % _ident, Name.Variable),
                (ur'%%%s%%' % _ident, Name.Variable),
                (r'%sT%s' % (_date, _time), Literal.Date),
                (_date, Literal.Date),
                (r'(\-|\+)?([0-9]+\.[0-9]+|\.([0-9])+)', Number.Float),
                (r'(\-|\+)?[0-9]+', Number.Integer),
                (ur'(%s)(\s*)(\()(?=.+?:\-)' % _ident, bygroups(Name.Function, Text, Punctuation)),
                (ur'(%s)(\s*)(\()(?!.+?:)' % _ident, bygroups(Name.Function, Text, Punctuation)),
                (_qname, QName),
                (_ident, Name),
                (r'<[^<>\"\{\}\`\\ ]+>', IRI),
                (r'[\(\),{}\|\.\^:\-\[\]\?]+', Punctuation),
                (r'/?=|<=?|>=?', Operator),
            ],
            'builtins': [
                (r'\b(association|association-role|base-locator|'
                 r'datatype|direct-instance-of|instance-of|item-identifier|'
                 r'object-id|occurrence|reifies|resource|role-player|'
                 r'scope|source-locator|subject-identifier|subject-locator|topic|'
                 r'topicmap|topic-name|type|value|value-like|variant)\b', Name.Builtin),
                (r'\b(count|not)\b', Name.Builtin),
            ],
            'multiline-comments': [
                (r'/\*', Comment.Multiline, '#push'),
                (r'\*/', Comment.Multiline, '#pop'),
                (r'[^/\*]+', Comment.Multiline),
                (r'[/*]', Comment.Multiline)
            ],
        }
