from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from viewpoint.settings import STAFF_ONLY, RELATION_MODELS, USE_APPROVAL

import datetime

if 'tagging' in settings.INSTALLED_APPS:
    import tagging
    from tagging.fields import TagField
    HAS_TAGGING = True
else:
    HAS_TAGGING = False

if 'categories' in settings.INSTALLED_APPS:
    from categories.models import Category
    HAS_CATEGORIES = True
else:
    HAS_CATEGORIES = False

if 'staff' in settings.INSTALLED_APPS:
    from staff.models import StaffMember as AuthorModel
else:
    from django.contrib.auth.models import User as AuthorModel

AUTHOR_LIMIT_CHOICES = {}

if STAFF_ONLY and not 'staff' in settings.INSTALLED_APPS:
    AUTHOR_LIMIT_CHOICES = {'is_staff': True}


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
    owners = models.ManyToManyField(AuthorModel, blank=True, limit_choices_to=AUTHOR_LIMIT_CHOICES)
    public = models.BooleanField(default=True)
    if HAS_CATEGORIES:
        category = models.ForeignKey(Category,related_name='viewpoint_categories',
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
        return ('viewpoint_blog_detail', None, {'slug': self.slug})
        
    class Meta:
        ordering = ('title',)
        get_latest_by = 'creation_date'


class EntryManager(models.Manager):
    def published(self, **kwargs):
        if USE_APPROVAL:
            kwargs.update(approved=True,public=True)
        else:
            kwargs.update(public=True)
        return self.filter(**kwargs)

class Entry(models.Model):
    blog = models.ForeignKey(Blog)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique_for_date='pub_date')
    author = models.ForeignKey(AuthorModel)
    credit = models.CharField(max_length=255,blank=True,null=True)
    photo = models.ImageField(null=True,blank=True,upload_to='photos/blog/entries/%Y/%m/%d/')
    tease = models.TextField()
    body = models.TextField()
    public = models.BooleanField(default=True)
    approved = models.BooleanField(default=not USE_APPROVAL)
    pub_date = models.DateField(auto_now_add=True)
    pub_time = models.TimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    if HAS_CATEGORIES:
        category = models.ForeignKey(Category,related_name='entry_categories',
                                        blank=True,null=True)
    if HAS_TAGGING:
        tags = TagField(blank=True, null=True)
    objects = EntryManager()
    
    class Meta:
        #unique_together = ('slug','pub_date')
        verbose_name_plural = _('Entries')
        get_latest_by = 'update_date'
        
    def __unicode__(self):
        return self.title
    
    def save(self, *a, **kw):
        if not self.slug:
            self.slug = slugify(self.title)[:50]
        if HAS_CATEGORIES:
            try:
                self.category = self.blog.category
            except ObjectDoesNotExist:
                pass
        self.update_date = datetime.datetime.now()
        super(Entry, self).save(*a, **kw)

    @models.permalink
    def get_absolute_url(self):
        return ('viewpoint_entry_detail', None, {
            'blog_slug': self.blog.slug,
            'year': self.pub_date.year,
            'month': self.pub_date.strftime('%b').lower(),
            'day': self.pub_date.day,
            'slug': self.slug
        })

if HAS_TAGGING:
    tagging.register(Blog)

if RELATION_MODELS:
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.contenttypes import generic
    
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
