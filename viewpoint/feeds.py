from datetime import datetime
from django.contrib.syndication.feeds import Feed
from django.contrib.syndication.views import Feed as FeedView
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.feedgenerator import Rss201rev2Feed, Atom1Feed
from viewpoint.settings import USE_CATEGORIES, DEFAULT_BLOG


from models import Entry, Blog

ENTRY_CONTENT_TYPE = ContentType.objects.get_for_model(Entry)

FEED_GENERATORS = getattr(settings, "FEED_GENERATORS", {
    'rss': Rss201rev2Feed,
    'atom': Atom1Feed
})

def LatestEntries(feed_title=None, feed_description=None, feed_link=None, 
    entry_count=20, feed_type='rss'):
    """Factory function for latest entries"""

    class _LatestEntries(Feed):
        def title(self):
            if not feed_title:
                return "Latest entries on %s" % Site.objects.get_current().name
            return feed_title
            
        def link(self):
            if not feed_link:
                return "/"
            return feed_link
            
        def description(self):
            if not feed_description:
                return "Latest entries on %s" % Site.objects.get_current().name
            return feed_description
    
        def items(self):
            return Entry.objects.published(
                ).order_by('-pub_date')[:entry_count]
        
        def item_pubdate(self, item):
            d = item.pub_date
            t = item.pub_time 
            dt = datetime(d.year, d.month, d.day, t.hour, t.minute, t.second)
            return dt
            
    feed_obj = _LatestEntries
    # Set the feed generator, default to rss.
    feed_obj.feed_type = FEED_GENERATORS.get(feed_type, Rss201rev2Feed)

    return feed_obj

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
    
    def LatestEntriesByCategory(feed_title=None, feed_description=None, 
        feed_link=None, entry_count=20, feed_type=None):
        
        class _LatestEntriesByCategory(Feed):

            def get_object(self, bits):
                if len(bits) < 1:
                    return Category.objects.all()[0]
                return Category.objects.get(slug=bits[-1])

            def title(self, obj):
                return feed_title or "My blog for category '%s'" % obj.name

            def link(self, obj):
                return feed_link or obj.get_absolute_url()

            def description(self, obj):
                return feed_decription or "Blog entries recently posted in category %s" % obj.name

            def items(self, obj):
                return Entry.objects.published(
                    category__slug=obj.slug).order_by('-pub_date')[:entry_count]


        feed_obj = _LatestEntriesByCategory
        # Set the feed generator, default to rss.
        feed_obj.feed_type = FEED_GENERATORS.get(feed_type, Rss201rev2Feed)

        return feed_obj

def LatestEntriesByBlog(feed_title=None, feed_description=None, 
    feed_link=None, entry_count=20, feed_type='rss' ):

    class _LatestEntriesByBlog(Feed):
        def get_object(self, bits):
            if len(bits) < 1 and DEFAULT_BLOG == '':
                return Blog.objects.all()[0]
            if DEFAULT_BLOG != '':
                return Blog.objects.get(slug__iexact=DEFAULT_BLOG, public=True)
            else:
                return Blog.objects.get(slug__iexact=bits[-1], public=True)
        
        def title(self, obj):
            return feed_title or "Latest entries for %s" % obj.title
        
        def link(self, obj):
            return feed_link or obj.get_absolute_url()
        
        def description(self, obj):
            return feed_description or "Latest entries posted for %s" % obj.title
        
        def items(self, obj):
            return Entry.objects.published(
                blog__pk=obj.pk).order_by('-pub_date')[:entry_count]
        
        def item_pubdate(self, item):
            d = item.pub_date
            t = item.pub_time
            dt = datetime(d.year, d.month, d.day, t.hour, t.minute, t.second)
            return dt
            
            
    feed_obj = _LatestEntriesByBlog
    # Set the feed generator, default to rss.
    feed_obj.feed_type = FEED_GENERATORS.get(feed_type, Rss201rev2Feed)

    return feed_obj

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
        return Entry.objects.published(
            blog__pk=obj.pk).order_by('-pub_date')[:15]
        
    def item_pubdate(self, item):
        d = item.pub_date
        t = item.pub_time
        dt = datetime(d.year, d.month, d.day, t.hour, t.minute, t.second)
        return dt