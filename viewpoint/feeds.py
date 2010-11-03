from datetime import datetime, timedelta
from django.contrib.syndication.feeds import Feed
from django.contrib.syndication.views import Feed as FeedView
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse, resolve
from viewpoint.settings import USE_CATEGORIES, DEFAULT_BLOG

from models import Entry, Blog

ENTRY_CONTENT_TYPE = ContentType.objects.get_for_model(Entry)

class LatestEntries(Feed):
    title = "Latest entries on %s" % Site.objects.get_current().name
    description = "Latest entries on %s" % Site.objects.get_current().name
    link = "/"
    
    def items(self):
        return Entry.objects.published().order_by('-pub_date')[:15]
        
    def item_pubdate(self, item):
        d = item.pub_date
        t = item.pub_time
        dt = datetime(d.year, d.month, d.day, t.hour, t.minute, t.second)
        return dt

class LatestEntriesView(FeedView):
    title = "Latest entries on %s" % Site.objects.get_current().name
    description = "Latest entries on %s" % Site.objects.get_current().name
    link = '/'
    
    def items(self):
        return Entry.objects.published().order_by('-pub_date')[:15]
        
    def item_pubdate(self, item):
        d = item.pub_date
        t = item.pub_time
        dt = datetime(d.year, d.month, d.day, t.hour, t.minute, t.second)
        return dt

if USE_CATEGORIES and 'categories' in settings.INSTALLED_APPS:
    from categories.models import Category
    
    class LatestEntriesByCategory(Feed):

        def get_object(self, bits):
            if len(bits) < 1:
                return Category.objects.all()[0]
            return Category.objects.get(slug=bits[-1])

        def title(self, obj):
            return "My blog for category '%s'" % obj.name

        def link(self, obj):
            return obj.get_absolute_url()

        def description(self, obj):
            return "Blog entries recently posted in category %s" % obj.name

        def items(self, obj):
            return Entry.objects.published(category__slug=obj.slug).order_by('-pub_date')[:10]


class LatestEntriesByBlog(Feed):
    def get_object(self, bits):
        if len(bits) < 1 and DEFAULT_BLOG == '':
            return Blog.objects.all()[0]
        if DEFAULT_BLOG != '':
            return Blog.objects.get(slug__iexact=DEFAULT_BLOG, public=True)
        else:
            return Blog.objects.get(slug__iexact=bits[-1], public=True)
        
    def title(self, obj):
        return "Latest entries for %s" % obj.title
        
    def link(self, obj):
        return obj.get_absolute_url()
        
    def description(self, obj):
        return "Latest entries posted for %s" % obj.title
        
    def items(self, obj):
        return Entry.objects.published(blog__pk=obj.pk).order_by('-pub_date')[:15]
        
    def item_pubdate(self, item):
        d = item.pub_date
        t = item.pub_time
        dt = datetime(d.year, d.month, d.day, t.hour, t.minute, t.second)
        return dt

class LatestEntriesByBlogView(Feed):
    def get_object(self, bits):
        if len(bits) < 1 and DEFAULT_BLOG == '':
            return Blog.objects.all()[0]
        if DEFAULT_BLOG != '':
            return Blog.objects.get(slug__iexact=DEFAULT_BLOG, public=True)
        else:
            return Blog.objects.get(slug__iexact=bits[-1], public=True)
        
    def title(self, obj):
        return "Latest entries for %s" % obj.title
        
    def link(self, obj):
        return obj.get_absolute_url()
        
    def description(self, obj):
        return "Latest entries posted for %s" % obj.title
        
    def items(self, obj):
        return Entry.objects.published(blog__pk=obj.pk).order_by('-pub_date')[:15]
        
    def item_pubdate(self, item):
        d = item.pub_date
        t = item.pub_time
        dt = datetime(d.year, d.month, d.day, t.hour, t.minute, t.second)
        return dt