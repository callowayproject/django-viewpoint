"""
URL routing for blogs, entries and feeds
"""

from django.conf.urls.defaults import patterns, url
from django.conf import settings
from feeds import LatestEntriesByBlog, LatestEntries #, EntryComments
from models import Blog
from views import generic_blog_entry_view, blog_detail
from viewpoint.settings import USE_CATEGORIES, DEFAULT_BLOG

FEEDS = {
    'all': LatestEntries,
    'latest': LatestEntries,
}

if USE_CATEGORIES and 'categories' in settings.INSTALLED_APPS:
    from feeds import LatestEntriesByCategory
    FEEDS['categories'] = LatestEntriesByCategory


urlpatterns = patterns('django.contrib.syndication.views',
    (r'^feeds/(?P<url>.*)/$', 'feed', {'feed_dict': FEEDS}),
)

urlpatterns += patterns('',
    # Blog detail (Main page of a blog, shows description and stuff)
    url(
        regex = r'^$', 
        view = blog_detail,
        name='viewpoint_blog_detail'
    ),
    # Listing of blog entries for a given year
    url(
        regex = r'^(?P<year>\d{4})/$', 
        view = generic_blog_entry_view, 
        name='viewpoint_blog_archive_year'
    ),
    # Listing of blog entries for a given month/year
    url(
        regex = r'^(?P<year>\d{4})/(?P<month>\w{3})/$', 
        view = generic_blog_entry_view, 
        name = 'viewpoint_blog_archive_month'
    ),
    # Listing of blog entries for a given week of the year
    url(
        regex = r'^(?P<year>\d{4})/(?P<week>\d{1,2})/$',
        view = generic_blog_entry_view,
        name = 'viewpoint_blog_archive_week'
    ),
    # Listing of blog entries for a given day
    url(
        regex = r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/$', 
        view = generic_blog_entry_view, 
        name = 'viewpoint_blog_archive_day'
    ),
    # Listing of blog entries for the current date
    url(
        regex = r'^today/$', 
        view = generic_blog_entry_view, 
        name='viewpoint_blog_archive_today'
    ),
    # A blog entry
    url(
        regex = r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$', 
        view = generic_blog_entry_view, 
        name='viewpoint_entry_detail'
    ),
    # A blog comments page
    url(
        regex = r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/comments/$', 
        view = generic_blog_entry_view,
        kwargs = {'template_name':'viewpoint/entry_comments.html'},
        name='viewpoint_entry_comments'
    ),
    # A blog printing page
    url(
        regex = r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/print/$', 
        view = generic_blog_entry_view, 
        kwargs = {'template_name':'viewpoint/entry_print.html'},
        name='viewpoint_entry_print'
    ),
    
)
