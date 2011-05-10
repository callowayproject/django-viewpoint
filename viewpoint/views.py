from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Q
from django.template.loader import select_template
from viewpoint.settings import DEFAULT_BLOG, MONTH_FORMAT
from django.views.generic.date_based import archive_day, archive_month, \
                                            archive_year, archive_today, \
                                            archive_week, object_detail

from models import Blog, Entry

def get_template(blog_slug, template_name):
    """
    Given a blog slug and template name (without the .html), this will return
    the appropriate template, looking in various directories.
    """
    return select_template((
            'viewpoint/%s/%s.html' % (blog_slug, template_name), 
            'viewpoint/%s.html' % template_name
        )).name

def generic_blog_entry_view(request, *args,  **kwargs):
    """
    A generic override for the default Django generic views 
    """
    blog_slug = kwargs.pop('blog_slug', DEFAULT_BLOG)
    if request.user.is_staff:
        queryset = Entry.objects.filter(blog__slug=blog_slug)
    else:
        queryset = Entry.objects.published(blog__slug=blog_slug)
    params = {
        'queryset': queryset,
        'date_field': 'pub_date',
        'allow_empty': True,
    }
    params.update(kwargs)
    
    if 'slug' in kwargs.keys():
        if 'template_name' not in params.keys():
            params['template_name'] = get_template(blog_slug, 'entry_detail')
            params['month_format'] = MONTH_FORMAT
        params.pop('allow_empty')
        return object_detail(request, **params)
    elif 'day' in kwargs.keys():
        if 'template_name' not in params.keys():
            params['template_name'] = get_template(blog_slug, 'entry_archive_day')
            params['month_format'] = MONTH_FORMAT
        return archive_day(request, **params)
    elif 'month' in kwargs.keys():
        if 'template_name' not in params.keys():
            params['template_name'] = get_template(blog_slug, 'entry_archive_month')
            params['month_format'] = MONTH_FORMAT
        return archive_month(request, **params)
    elif 'week' in kwargs.keys():
        if 'template_name' not in params.keys():
            params['template_name'] = get_template(blog_slug, 'entry_archive_week')
        return archive_week(request, **params)
    elif 'year' in kwargs.keys():
        if 'template_name' not in params.keys():
            params['template_name'] = get_template(blog_slug, 'entry_archive_year')
        return archive_year(request, **params)
    else:
        if 'template_name' not in params.keys():
            params['template_name'] = get_template(blog_slug, 'entry_archive_today')
        return archive_today(request, **params)


def blog_detail(request, blog_slug=DEFAULT_BLOG):
    """
    Return the blog_detail page for the specified blog.
    """
    blog = get_object_or_404(Blog, slug=blog_slug, public=True)
    return render_to_response(get_template(blog_slug, 'blog_detail'), {
            'object':blog,
        }, context_instance=RequestContext(request))

def feeds_index(request, template_name='viewpoint/feeds_index.html'):
    blogs = Blog.objects.filter(public=True).order_by('title')
    return render_to_response(template_name,
                              {'blogs': blogs},
                              context_instance=RequestContext(request))
    
