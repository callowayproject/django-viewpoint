from datetime import datetime, timedelta
from django.contrib.syndication.feeds import Feed
from categories.models import Category
from models import Entry, Blog

from mptt_comments.models import MpttComment
from django.contrib.contenttypes.models import ContentType

ENTRY_CONTENT_TYPE = ContentType.objects.get_for_model(Entry)

class EntryComments(Feed):
    def get_object(self, bits):
        if len(bits) < 1:
            return Blog.objects.all()[0]
        return Blog.objects.get(slug__iexact=bits[-1], public=True)
    
    def title(self, obj):
        return "Neighborhood comments for '%s'" % obj.title
        
    def link(self, obj):
        return obj.get_absolute_url()
    
    def description(self, obj):
        return "Latest entry comments posted for neighborhood %s" % obj.title
        
    def items(self, obj):
        nids = []
        for i in Entry.objects.published().filter(blog__pk=obj.pk).values('pk'):
            for k,v in i.items():
                nids.append(str(v))
                
        return MpttComment.objects.filter(is_public=True, is_removed=False, 
            content_type__pk=ENTRY_CONTENT_TYPE.pk, 
            object_pk__in=nids).exclude(parent=None).order_by('-submit_date')[:15]
        
    def item_link(self, item):
        return item.content_object.get_absolute_url()
        
    def item_guid(self, item):
        return item.get_absolute_url()
        
    def item_pubdate(self, item):
        return item.submit_date
        
        
class LatestEntries(Feed):
    title = "Latest entires from our community"
    link = "/neighborhood/"
    description = "Recent blog activity from all neighborhoods"

    def items(self):
        start = datetime.now() - timedelta(days=7)
        return Entry.objects.published().filter(pub_date__gte=start).order_by('-pub_date')
        
    def item_pubdate(self, item):
        d = item.pub_date
        t = item.pub_time
        dt = datetime(d.year, d.month, d.day, t.hour, t.minute, t.second)
        return dt
       
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
        if len(bits) < 1:
            return Blog.objects.all()[0]
        return Blog.objects.get(slug__iexact=bits[-1], public=True)
        
    def title(self, obj):
        return "Latest entries for neighborhood %s" % obj.title
        
    def link(self, obj):
        return obj.get_absolute_url()
        
    def description(self, obj):
        return "Latest entries posted for neighborhood %s" % obj.title
        
    def items(self, obj):
        return Entry.objects.published(blog__pk=obj.pk).order_by('-pub_date')[:15]
        
    def item_pubdate(self, item):
        d = item.pub_date
        t = item.pub_time
        dt = datetime(d.year, d.month, d.day, t.hour, t.minute, t.second)
        return dt