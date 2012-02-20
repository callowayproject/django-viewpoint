"""
URL routing for blogs, entries and feeds
"""

from django.conf.urls.defaults import patterns, url
from django.conf import settings
from feeds import LatestEntriesByBlog, LatestEntries
from models import Blog
from views import generic_blog_entry_view, blog_detail
from viewpoint.settings import USE_CATEGORIES, URL_REGEXES, DEFAULT_BLOG

FEEDS = {
    'all': LatestEntries(),
    'latest': LatestEntriesByBlog(),
}

if USE_CATEGORIES and 'categories' in settings.INSTALLED_APPS:
    from feeds import LatestEntriesByCategory
    FEEDS['categories'] = LatestEntriesByCategory()


urlpatterns = patterns('django.contrib.syndication.views',
    (r'^feeds/(?P<url>.*)/$', 'feed', {'feed_dict': FEEDS}),
)

if DEFAULT_BLOG == '':
    urlpatterns += patterns('',
        # Blog Index (listing of all public blogs)
        url(
            regex = r'^$',
            view = 'django.views.generic.list_detail.object_list',
            kwargs = {
                'template_name': 'viewpoint/index.html',
                'queryset': Blog.objects.filter(public=True)},
            name = "viewpoint_blog_index"
        ),
    )

urlpatterns += patterns('',
    # Blog detail (Main page of a blog, shows description and stuff)
    url(
        regex = URL_REGEXES['blog'], 
        view = blog_detail,
        name='viewpoint_blog_detail'
    ),
    # Listing of blog entries for a given year
    url(
        regex = URL_REGEXES['year'], 
        view = generic_blog_entry_view, 
        name='viewpoint_blog_archive_year'
    ),
    # Listing of blog entries for a given month/year
    url(
        regex = URL_REGEXES['month'], 
        view = generic_blog_entry_view, 
        name = 'viewpoint_blog_archive_month'
    ),
    # Listing of blog entries for a given day
    url(
        regex = URL_REGEXES['day'], 
        view = generic_blog_entry_view, 
        name = 'viewpoint_blog_archive_day'
    ),
    # Listing of blog entries for the current date
    url(
        regex = r'%stoday/$' % URL_REGEXES['blog'].rstrip("$"), 
        view = generic_blog_entry_view, 
        name='viewpoint_blog_archive_today'
    ),
    # A blog entry
    url(
        regex = URL_REGEXES['entry'], 
        view = generic_blog_entry_view, 
        name='viewpoint_entry_detail'
    ),
    # A blog comments page
    url(
        regex = r'%scomments/$' % URL_REGEXES['entry'].rstrip("$"), 
        view = generic_blog_entry_view,
        kwargs = {'template_name':'viewpoint/entry_comments.html'},
        name='viewpoint_entry_comments'
    ),
    # A blog printing page
    url(
        regex = r'%sprint/$' % URL_REGEXES['entry'].rstrip("$"), 
        view = generic_blog_entry_view, 
        kwargs = {'template_name':'viewpoint/entry_print.html'},
        name='viewpoint_entry_print'
    ),
)
