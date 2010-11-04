from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
from viewpoint.feeds import LatestEntriesView, LatestEntries, LatestEntriesByBlog

rss_feeds = {
    'latest': LatestEntries(feed_type='rss'),
    'blog': LatestEntriesByBlog(feed_type='rss')
}
atom_feeds = {
    'latest': LatestEntries(feed_type='atom'),
    'blog': LatestEntriesByBlog(feed_type='atom')
}

urlpatterns = patterns('',
    # Uncomment for Multiple blogs
    #(r'^blogs/', include('viewpoint.urls')),
    #Uncomment for One blog
    (r'^blogs/', include('viewpoint.urls')),
    (r'^feeds/all/$', LatestEntriesView()),
    
    (r'^rss/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': rss_feeds}),
    (r'^atom/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': atom_feeds}),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
)
