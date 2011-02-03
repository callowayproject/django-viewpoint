# -*- coding: utf-8 -*-
"""Metaweblog publishing via XMLRPC.

This is a heavily modified version of the example code found at Greg Abbas' 
blog [http://www.allyourpixel.com/post/metaweblog-38-django/ All Your Pixel]

:Authors:
    - Greg Abbas
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

from threaded_multihost import threadlocals
from banjo.blog.models import *
from banjo.blog.syndication.common.decorators import xml_auth_by_token
from banjo.blog.syndication.common.pub import ResourceNotFoundException, format_date, date_from_iso8601
from banjo.blog.syndication.mt.pub import mt_post_struct, mt_edit_post
from django.conf import settings
from django.core import urlresolvers
from django.utils.translation import gettext as _
from django_xmlrpc.decorators import xmlrpc_func, AuthenticationFailedException, PermissionDeniedException
import datetime
        
def post_struct(post):
    link = post.blog.full_url(post.get_absolute_url())
    categories = post.categories.all()
    
    struct = {
        'postid': post.tag_uri,
        'title': post.headline,
        'link': link,
        'permaLink': link,
        'description': post.raw_excerpt,
        'categories': [c.name for c in categories],
        'userid': post.authors.all()[0].user.username,
    }
    
    struct.update(mt_post_struct(post))
        
    if post.pub_date:
        struct['dateCreated'] = format_date(post.pub_date)
    return struct

# ------ XMLRPC methods ------

@xml_auth_by_token()
@xmlrpc_func(returns='bool', args=['string', 'string', 'string', 'struct', 'bool'])
def edit_post(user, postid, struct, publish):
    return _edit_post(user, postid, struct, publish)
    
def _edit_post(author, postid, struct, publish):
    try:
        post = Post.objects.get(tag_uri=postid)
        if not post.blog.is_author(author):
            log.debug("Author '%s' cannot delete post: %s", author.user.username, postid)
            raise PermissionDeniedException()

        log.debug("Author '%s' editing post: %s", author.user.username, postid)    
        
        post = mt_edit_post(struct, post)
        
        title = struct.get('title', None)
        if title is not None:
            post.headline = title

        excerpt = struct.get('description', None)
        if excerpt is not None:
            post.raw_excerpt = excerpt

        if publish:
            post.status = POST_PUBLISHED
        else:
            post.status = POST_DRAFT
            
        post.set_categories_by_name(struct.get('categories', []))
        
        threadlocals.set_current_user(author.user)
        post.save()
        
        return True
        
    except Post.DoesNotExist:
        log.debug("Could not find post: %s", postid)
        raise ResourceNotFoundException()

@xml_auth_by_token()
@xmlrpc_func(returns='struct', args=['string', 'string', 'string'])
def get_categories(author, blogid):
    return _get_categories(author, blogid)
    
def _get_categories(author, blogid):
    blog = Blog.objects.by_slug(blogid)
    if not blog:
        raise ResourceNotFoundException()

    if not blog.is_author(author):
        raise PermissionDeniedException()

    structs = []
    for cat in Category.objects.enabled_for_user(blog, user=author.user):
        rssurl = urlresolvers.reverse('banjo_atom_tag_feed', None, { 'blog' : blog.slug, 'url' : cat.key})
        htmlurl = urlresolvers.reverse('banjo_tag_index', None, { 'blog' : blog.slug, 'path' : cat.key})
        rssurl = blog.full_url(rssurl)
        htmlurl = blog.full_url(htmlurl)
        
        structs.append({
            'categoryName' : cat.key,
            'description' : cat.key,
            'htmlUrl' : htmlurl,
            'rssUrl' : rssurl
        })
    return structs

@xml_auth_by_token()
@xmlrpc_func(returns='array', args=['string', 'string', 'string', 'string', 'int'])
def get_recent_posts(author, blogid, num_posts):
    return _get_recent_posts(author, blogid, num_posts)
    
def _get_recent_posts(author, blogid, num_posts):
    
    blog = Blog.objects.by_slug(blogid)
    if not blog:
        raise ResourceNotFoundException()
    
    if not blog.is_author(author):
        raise PermissionDeniedException()
           
    return [post_struct(post) for post in blog.latest(count=num_posts)]

@xml_auth_by_token()
@xmlrpc_func(returns='struct', args=['string', 'string', 'string', 'string'])
def get_post(user, postid):
    return _get_post(user, postid)
    
def _get_post(user, postid):
    try:
        post = Post.objects.get(tag_uri=postid)
        return post_struct(post)

    except Post.DoesNotExist:
        raise ResourceNotFoundException()

@xml_auth_by_token()
@xmlrpc_func(returns='struct', args=['string', 'string', 'string', 'struct'])
def new_media_object(user, blogid, struct):
    return _new_media_object(user, blogid, struct)
    
def _new_media_object(user, blogid, struct):
    # The input struct must contain at least three elements, name,
    # type and bits. returns struct, which must contain at least one
    # element, url
    mime = struct['type']
    bits = struct['bits']
    name = struct['name']

    f = open("%s/%s" % (settings.MEDIA_ROOT, name), 'w')
    f.write("%s" % bits)
    f.close()

    return {'url': "%s/%s" % (settings.MEDIA_URL, name)}

@xml_auth_by_token()
@xmlrpc_func(returns='string', args=['string', 'string', 'string', 'bool'])
def new_post(author, blogid, struct, publish):
    return _new_post(author, blogid, struct, publish)
    
def _new_post(author, blogid, struct, publish):
    blog = Blog.objects.by_slug(blogid)
    if not blog:
        raise ResourceNotFoundException()
    
    if not blog.is_author(author):
        raise PermissionDeniedException()
    
    if publish:
        status = POST_PUBLISHED
    else:
        status = POST_DRAFT

    title = struct.get('title', None)
    if title is None:
        title = datetime.datetime.now().isoformat()
    
    rawdate = struct['dateCreated']
    dt = date_from_iso8601(rawdate)
    
    post = Post(headline = title,
                create_date = dt,
                status = status,
                blog = blog,
                )

    post = mt_edit_post(struct, post)

    excerpt = struct.get('description', None)
    if excerpt is not None:
        post.raw_excerpt = excerpt

    threadlocals.set_current_user(author.user)
    post.save()
    post.set_categories_by_name(struct.get('categories', []))
    
    return post.tag_uri

