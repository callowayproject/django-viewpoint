from django.views.generic.date_based import archive_day, archive_month, archive_year, object_detail
from django.conf.urls.defaults import *
from feeds import LatestEntriesByBlog, LatestEntriesByCategory, LatestEntries, EntryComments
from models import Blog, Entry

def generic_blog_entry_view(blog_slug, year, month=None, day=None, slug=None, **kwargs):
    queryset = Entry.objects.filter(blog__slug=blog_slug)
    params = {
        'queryset': queryset,
        'year': year,
        'month': month,
        'day': day,
        'slug': slug,
    }
    params.update(kwargs)
    if month and day and slug:
        return object_detail(**params)
    elif month and day:
        return archive_day(**params)
    elif month:
        return archive_month(**params)
    else:
        return archive_year(**params)

feeds = {
    'all': LatestEntries,
    'latest': LatestEntriesByBlog,
    'categories': LatestEntriesByCategory,
    'comments': EntryComments,
}


urlpatterns = patterns('django.contrib.syndication.views',
    (r'^feeds/(?P<url>.*)/$', 'feed', {'feed_dict': feeds}),
)

urlpatterns += patterns('',
    url(r'^(?P<blog_slug>[-\w]+)/(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$', 
        generic_blog_entry_view, 
        name='viewpoint_entry_detail'),
    url(r'^(?P<slug>[-\w]+)/(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/$', 
        generic_blog_entry_view, 
        name='viewpoint_archive_day'),
    url(r'^(?P<slug>[-\w]+)/(?P<year>\d{4})/(?P<month>\w{3})/$', 
        generic_blog_entry_view, 
        name='viewpoint_archive_month'),
    url(r'^(?P<slug>[-\w]+)/(?P<year>\d{4})/$', 
        generic_blog_entry_view, 
        name='viewpoint_archive_year'),
    url(r'^(?P<slug>[-\w]+)/$', 
        'django.views.generic.list_detail.object_detail', 
        name='viewpoint_detail'),
)
