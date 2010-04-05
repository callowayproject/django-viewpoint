from django.conf.urls.defaults import *
from feeds import LatestEntriesByBlog, LatestEntriesByCategory, LatestEntries, EntryComments

feeds = {
    'all': LatestEntries,
    'latest': LatestEntriesByBlog,
    'categories': LatestEntriesByCategory,
    'comments': EntryComments,
}


urlpatterns = patterns('django.contrib.syndication.views',
    (r'^feeds/(?P<url>.*)/$', 'feed', {'feed_dict': feeds}),
)

urlpatterns += patterns('blog.views',
    url(r'^(?P<blog_slug>[-\w]+)/(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$', 'entry_detail', name='blog_entry_detail'),
    url(r'^(?P<slug>[-\w]+)/(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/$', 'archive_day', name='blog_archive_day'),
    url(r'^(?P<slug>[-\w]+)/(?P<year>\d{4})/(?P<month>\w{3})/$', 'archive_month', name='blog_archive_month'),
    url(r'^(?P<slug>[-\w]+)/(?P<year>\d{4})/$', 'archive_year', name='blog_archive_year'),
    url(r'^(?P<slug>[-\w]+)/$', 'blog_detail', name='blog_detail'),
)
