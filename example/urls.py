from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
from viewpoint.feeds import LatestEntriesView

urlpatterns = patterns('',
    # Uncomment for Multiple blogs
    #(r'^blogs/', include('viewpoint.urls')),
    #Uncomment for One blog
    (r'^blogs/', include('viewpoint.urls')),
    (r'^feeds/all/$', LatestEntriesView()),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
)
