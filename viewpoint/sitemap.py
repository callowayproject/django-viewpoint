from django.contrib.sitemaps import Sitemap
from models import Entry

class BlogSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Entry.objects.published().order_by('-update_date')

    def lastmod(self, obj):
        return obj.pub_date
