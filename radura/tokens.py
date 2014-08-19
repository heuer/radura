# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 - 2014 -- Lars Heuer - Semagia <http://www.semagia.com/>.
# All rights reserved.
#
# BSD license.
#
"""\
Token names which are not provided by Pygments.

:author:       Lars Heuer (heuer[at]semagia.com)
:organization: Semagia - http://www.semagia.com/
:license:      BSD license
"""
from pygments.token import Literal, Name

IRI = Literal
QName = Name
Wildcard = Name.Variable.Instance

if False:
    IRI = Literal.IRI
    QName = Name.QName
