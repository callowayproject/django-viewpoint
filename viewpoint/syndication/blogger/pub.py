# -*- coding: utf-8 -*-
"""Blogger publishing via XMLRPC.

This is a heavily modified version of the example code found at Greg Abbas' 
blog [http://www.allyourpixel.com/post/metaweblog-38-django/ All Your Pixel]

:Authors:
    - Greg Abbas
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

from banjo.blog.syndication.common.decorators import xml_auth_by_token
from banjo.blog.models import Blog, Post
from banjo.blog.syndication.common.pub import ResourceNotFoundException, format_date
from datetime import datetime
from django_xmlrpc.decorators import xmlrpc_func, AuthenticationFailedException, PermissionDeniedException
import logging, re

log = logging.getLogger('syndication.blogger')

@xml_auth_by_token(pos=2)
@xmlrpc_func(returns='bool', args=['string', 'string', 'string', 'string', 'bool'])
def delete_post(author, appkey, postid, publish):
    return do_delete_post(author, appkey, postid, publish)
    
def do_delete_post(author, appkey, postid, publish):
    try:
        post = Post.objects.get(tag_uri=postid)
        if post.blog.is_author(author):
            log.debug("Author '%s' deleting post: %s", author.user.username, post.slug)
            post.delete()
        else:
            log.debug("Author '%s' cannot delete post: %s", author.user.username, postid)
            raise PermissionDeniedException()
    except Post.DoesNotExist:
        raise ResourceNotFoundException()
        
    return True
    
@xml_auth_by_token()
@xmlrpc_func(returns='struct', args=['string', 'string', 'string'])
def get_user_info(author, appkey):
    return do_get_user_info(author, appkey)

def do_get_user_info(author, appkey):
    """
    Get a struct with user info
    """
    return {
        'userid' : author.id,
        'firstname' : getattr(author.user, 'first_name', ''),
        'lastname' : getattr(author.user, 'last_name', ''),
        'nickname' : author.user.username,
        'email' : author.user.email,
        'url' : author.get_absolute_url()
    }

@xml_auth_by_token()
@xmlrpc_func(returns='array', args=['string', 'string', 'string'])
def get_users_blogs(author, appkey):
    return do_get_users_blogs(author, appkey)

def do_get_users_blogs(author, appkey):
    """
    an array of <struct>'s containing the ID (blogid), name
    (blogName), and URL (url) of each blog.
    """
    log.debug('get_users_blogs author=%s, appkey=%s', author, appkey)
    blogs = Blog.objects.filter(authors__in=(author,))
    return [{
            'blogid': blog.slug,
            'blogName': blog.name,
            'url': blog.get_absolute_url(),
            } for blog in blogs]

@xml_auth_by_token(pos=2)
@xmlrpc_func(returns='bool', args=['string', 'string', 'string', 'string', 'string', 'bool'])
def new_post(author, appkey, blogid, content, publish):
    return do_new_post(author, appkey, blogid, content, publish)

def do_new_post(author, appkey, postid, content, publish):
    blog = Blog.objects.by_slug(blogid)
    if not blog:
        raise ResourceNotFoundException()

    if not blog.is_author(author):
        raise PermissionDeniedException()

    titlepat = re.compile(r'<title>(.*)</title>')
    match = titlepat.search(content)
    if m:
        title = m.group(1)
        content = content[:m.start()] + content[m.end():]
    else:
        title = ''
        
    body = content

    if publish:
        status = POST_PUBLISHED
    else:
        status = POST_DRAFT

    dt = datetime.now()

    post = Post(headline = title,
                raw_body = body,
                create_date = dt,
                status = status,
                blog = blog,
                )

    post.save()
    post.authors.add(author)
    post.tags = struct.get('categories', [])
    return post.tag_uri