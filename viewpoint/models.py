from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import get_storage_class

from viewpoint.settings import STAFF_ONLY, ENTRY_RELATION_MODELS, USE_APPROVAL, \
                                BLOG_RELATION_MODELS, DEFAULT_STORAGE

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

IMAGE_STORAGE = get_storage_class(DEFAULT_STORAGE)

class BlogManager(models.Manager):
    def published(self, **kwargs):
        kwargs.update(public=True)
        return self.filter(**kwargs)

class Blog(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    tease = models.TextField(blank=True)
    photo = models.ImageField(
        null=True,
        blank=True,
        storage=IMAGE_STORAGE(),
        upload_to='viewpoint/blog/%Y/%m/%d/')
    owners = models.ManyToManyField(AuthorModel, blank=True, limit_choices_to=AUTHOR_LIMIT_CHOICES)
    public = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    if HAS_CATEGORIES:
        category = models.ForeignKey(Category,related_name='viewpoint_categories',
                                        blank=True,null=True)
    alternate_title = models.CharField(
        blank=True,
        default="",
        max_length=100,
        help_text="An alternative title to use on pages with this category."
    )
    description = models.TextField(blank=True, null=True)
    meta_keywords = models.CharField(
        blank=True,
        null=True,
        default="",
        max_length=255,
        help_text="Comma-separated keywords for search engines.")
    meta_extra = models.TextField(
        blank=True,
        null=True,
        default="",
        help_text="(Advanced) Any additional HTML to be placed verbatim in the &lt;head&gt;")
    
    objects = BlogManager()
    
    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:50]
        for entry in self.entry_set.all():
            entry.public = self.public
            entry.save()
        super(Blog, self).save(*args, **kwargs)

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
        kwargs.update(pub_date__lte=datetime.date.today())
        return self.filter(**kwargs)

class Entry(models.Model):
    blog = models.ForeignKey(Blog)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique_for_date='pub_date')
    author = models.ForeignKey(AuthorModel)
    credit = models.CharField(max_length=255,blank=True,null=True)
    photo = models.ImageField(
        null=True,
        blank=True,
        storage=IMAGE_STORAGE(),
        upload_to='viewpoint/entry/%Y/%m/%d/')
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
        unique_together = ('blog','pub_date','slug')
        verbose_name_plural = _('Entries')
        get_latest_by = 'update_date'
        ordering = ('-pub_date', '-pub_time',)
        
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

if ENTRY_RELATION_MODELS:
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.contenttypes import generic
    
    RELATIONS = [Q(app_label=al, model=m) for al, m in [x.split('.') for x in ENTRY_RELATION_MODELS]]
    
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

if BLOG_RELATION_MODELS:
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.contenttypes import generic
    
    RELATIONS = [Q(app_label=al, model=m) for al, m in [x.split('.') for x in BLOG_RELATION_MODELS]]
    
    blog_relation_limits = reduce(lambda x,y: x|y, RELATIONS)
    class BlogRelation(models.Model):
        """Related blog item"""
        blog = models.ForeignKey(Blog)
        content_type = models.ForeignKey(ContentType, limit_choices_to=blog_relation_limits)
        object_id = models.PositiveIntegerField()
        content_object = generic.GenericForeignKey('content_type', 'object_id')
        relation_type = models.CharField(_("Relation Type"), 
            max_length="200", 
            blank=True, 
            null=True,
            help_text=_("A generic text field to tag a relation, like 'leadphoto'."))
            
        def __unicode__(self):
            return u"BlogRelation"

    