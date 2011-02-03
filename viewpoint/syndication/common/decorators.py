# -*- coding: utf-8 -*-
"""Provides decorators used for syndication views.

:Authors:
    - Bruce Kroeze
"""
"""
New BSD License
===============
Copyright (c) 2008, Bruce Kroeze http://coderseye.com

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.
    * Neither the name of SolidSiteSolutions LLC, Zefamily LLC nor the names of its 
      contributors may be used to endorse or promote products derived from this 
      software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
__docformat__="restructuredtext"

from django.conf import settings
from banjo.blog.decorators import validate_author_by_token
from django_xmlrpc.decorators import AuthenticationFailedException
import logging
log = logging.getLogger('xml.common.decorators')

def xml_auth_by_token(pos=1):
    """
    A decorator which allows non-persistent login via token.
    Assumes user is arg #`pos` and password is `pos`+1.
    
    Sends the original arguments to the wrapped function, with `Author` as the first argument.
    """

    def _decorate(func):
        def _wrapper(*args, **kwargs):
            username = args[pos+0]
            password = args[pos+1]
            if settings.DEBUG:
                log.debug('xml_auth_by_token: %i args, pos=%i, %s=%s', len(args), pos, username, password)
            try:
                author = validate_author_by_token(username, password)
            except ValueError:
                raise AuthenticationFailedException()
                
            args = args[0:pos]+args[pos+2:]
            return func(author, *args, **kwargs)

        return _wrapper
    return _decorate