# -*- coding: utf-8 -*-
"""MT publishing via XMLRPC.

:Authors:
    - Bruce Kroeze
"""
"""
New BSD License
===============
Copyright (c) 2008, Bruce Kroeze http://solidsitesolutions.com

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

from banjo.blog.models import *
from banjo.blog.syndication.common.decorators import xml_auth_by_token
from banjo.blog.syndication.common.pub import ResourceNotFoundException
from django.conf import settings
from django.core import urlresolvers
from django.utils.translation import gettext as _
from django_xmlrpc.decorators import xmlrpc_func, AuthenticationFailedException, PermissionDeniedException
import satchmo.configuration as config

MARKUP_NONE = '0'
MARKUP_LINEBREAK = '1'
MARKUP_TEXTILE = '2'
MARKUP_RESTRUCTUREDTEXT = '3'
MARKUP_MARKDOWN = '4'

MARKUP_DICT = {
    'raw' : '0',
    'linebreak' : '1',
    'textile' : '2',
    'restructuredtext' : '3',
    'markdown' : '4'
}

def mt_edit_post(struct, post):
    """Apply MT extensions to the post."""
    summary = struct.get('mt_excerpt', None)
    if summary is not None:
        post.raw_summary = summary
        
    body = struct.get('mt_text_more', None)
    if body is not None:
        post.raw_body = body
    
    format = struct.get('mt_convert_breaks', '0')
    format = mt_format_to_key(format)
    post.markup = format
    # force true/false for Postgres
    comments = struct.get('mt_allow_comments', False) == True
    post.enable_comments = comments
    # force true/false for Postgres
    pings = struct.get('mt_allow_pings', False) == True
    post.enable_pings = pings
        
    return post

def mt_post_struct(post):
    """Return MT extensions to the post struct for Metaweblog."""
    
    format = mt_format_from_key(post.markup)
    return {
        'mt_excerpt': post.raw_summary,
        'mt_text_more': post.raw_body,
        'mt_convert_breaks' : format,
        'mt_allow_comments': post.enable_comments,
        'mt_allow_pings': post.enable_pings,
    }

def mt_format_from_key(key):
    return MARKUP_DICT[key]
    
def mt_format_to_key(val):
    for k, v in MARKUP_DICT.items():
        if v == val:
            return k
    return "raw"

@xml_auth_by_token()
@xmlrpc_func(returns='array', args=['string', 'string', 'string'])
def get_category_list(author, blogid):
    return do_get_category_list(author, blogid)
    
def do_get_category_list(author, blogid):
    blog = Blog.objects.by_slug(blogid)
    if not blog:
        raise ResourceNotFoundException()

    if not blog.is_author(author):
        raise PermissionDeniedException()

    structs = []
    for cat in blog.categories.all():
        structs.append({
            'categoryName' : cat.longname,
            'categoryId' : cat.key,
        })
    return structs

@xml_auth_by_token()
@xmlrpc_func(returns='array', args=['string', 'string', 'string'])
def get_post_categories(author, postid):
    return do_get_post_categories(author, postid)

def do_get_post_categories(author, postid):
    post = None
    if postid:
        try:
            post = Post.objects.get(tag_uri__exact = postid)
        except Post.DoesNotExist:
            pass
    
    if not post:
        raise ResourceNotFoundException()
        
    if not post.blog.is_author(author):
        raise PermissionDeniedException()

    structs = []
    for tag in post.tags:
        structs.append({
            'categoryName' : tag.name,
            'categoryId' : tag.name,
            'isPrimary' : False
        })
    return structs

@xml_auth_by_token()
@xmlrpc_func(returns='array', args=['string', 'string', 'string', 'array'])
def set_post_categories(author, postid, categories):
    return do_set_post_categories(author, postid, categories)

def do_set_post_categories(author, postid, categories):
    post = None
    if postid:
        try:
            post = Post.objects.get(tag_uri=postid)
        except Post.DoesNotExist:
            pass

    if not post:
        raise ResourceNotFoundException()

    if not post.blog.is_author(author):
        raise PermissionDeniedException()

    cats = [cat['categoryId'] for cat in categories]
    post.tags = cats

    return True

@xmlrpc_func(returns='struct', args=[])
def supported_text_filters():
    return do_supported_text_filters()
    
def do_supported_text_filters():
    structs = [
        {'key': MARKUP_NONE, 'label' : 'Leave Text Untouched'},
        {'key': MARKUP_LINEBREAK, 'label' : 'Convert Line Breaks'},
    ]
    formats = config.config_value('BLOG', 'MARKUP_ENGINES')
    if 'textile' in formats:
        structs.append({'key': MARKUP_TEXTILE, 'label' : 'Use Textile'})
        
    if 'restructuredtext' in formats:
        structs.append({'key': MARKUP_RESTRUCTUREDTEXT, 'label' : 'Use RestructuredText'})
    
    if 'markdown' in formats:
        structs.append({'key': MARKUP_MARKDOWN, 'label' : 'Use Markdown'})
    
    return structs
