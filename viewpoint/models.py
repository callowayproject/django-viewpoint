from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from categories.models import Category
import tagging
from tagging.fields import TagField

try:
    from staff.models import StaffMember as AuthorModel
except ImportError:
    from django.contrib.auth.models import User as AuthorModel

class BlogManager(models.Manager):
    def published(self, **kwargs):
        kwargs.update(public=True)
        return self.filter(**kwargs)

class Blog(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    tease = models.TextField()
    description = models.TextField()
    photo = models.ImageField(null=True,blank=True,upload_to='photos/blog/%Y/%m/%d/')
    owner = models.ManyToManyField(AuthorModel, blank=True)
    public = models.BooleanField(default=True)
    category = models.ForeignKey(Category,related_name='blog_categories',
                                        blank=True,null=True)
    
    objects = BlogManager()
    
    def __unicode__(self):
        return self.title

    def save(self, *a, **kw):
        if not self.slug:
            self.slug = slugify(self.title)[:50]
        super(Blog, self).save(*a, **kw)

    @models.permalink
    def get_absolute_url(self):
        return ('blog_detail', None, {'slug': self.slug})
        
    class Meta:
        ordering = ('title',)
        get_latest_by = 'creation_date'


class EntryManager(models.Manager):
    def published(self, **kwargs):
        kwargs.update(approved=True,public=True)
        return self.filter(**kwargs)

class Entry(models.Model):
    pub_date = models.DateField(auto_now_add=True)
    pub_time = models.TimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique_for_date='pub_date')
    tease = models.TextField()
    photo = models.ImageField(null=True,blank=True,upload_to='photos/blog/entries/%Y/%m/%d/')
    credit = models.CharField(max_length=255,blank=True,null=True)
    body = models.TextField()
    public = models.BooleanField(default=True)
    approved = models.BooleanField(default=False)
    author = models.ForeignKey(AuthorModel)
    blog = models.ForeignKey(Blog)
    category = models.ForeignKey(Category,related_name='entry_categories',
                                        blank=True,null=True)
    tags = TagField(blank=True, null=True)
    objects = EntryManager()
    
    class Meta:
        unique_together = ('slug','pub_date')
        verbose_name_plural = _('Entries')
        get_latest_by = 'update_date'
        
    def __unicode__(self):
        return self.title
    
    def save(self, *a, **kw):
        if not self.slug:
            self.slug = slugify(self.title)[:50]
        self.category = self.blog.category
        super(Entry, self).save(*a, **kw)

    @models.permalink
    def get_absolute_url(self):
        return ('blog_entry_detail', None, {
            'blog_slug': self.blog.slug,
            'year': self.pub_date.year,
            'month': self.pub_date.strftime('%b').lower(),
            'day': self.pub_date.day,
            'slug': self.slug
        })
        
tagging.register(Blog)
#tagging.register(Entry)

from django.conf import settings

if hasattr(settings, 'ENTRY_RELATION_MODELS'):
    from django.db.models import Q
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.contenttypes import generic
    
    RELATION_MODELS = getattr(settings, 'ENTRY_RELATION_MODELS', [])
    RELATIONS = [Q(app_label=al, model=m) for al, m in [x.split('.') for x in RELATION_MODELS]]
    
    entry_relation_limits = reduce(lambda x,y: x|y, RELATIONS)
    class EntryRelation(models.Model):
        """Related entry item"""
        entry = models.ForeignKey(Entry)
        content_type = models.ForeignKey(ContentType, limit_choices_to=entry_relation_limits)
        object_id = models.PositiveIntegerField()
        content_object = generic.GenericForeignKey('content_type', 'object_id')
        relation_type = models.CharField(_("Relation Type"), 
            max_length="200", 
            blank=True, 
            null=True,
            help_text=_("A generic text field to tag a relation, like 'leadphoto'."))

        def __unicode__(self):
            return u"EntryRelation"
    

