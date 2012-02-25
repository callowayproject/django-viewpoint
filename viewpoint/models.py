import datetime

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import get_storage_class
from django.core.files.images import get_image_dimensions
from django.db import models
from django.db.models import Q
from django.db.models.loading import get_model
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from .settings import (STAFF_ONLY, ENTRY_RELATION_MODELS, USE_APPROVAL,
                                BLOG_RELATION_MODELS, DEFAULT_STORAGE,
                                USE_CATEGORIES, USE_TAGGING, AUTHOR_MODEL, 
                                DEFAULT_BLOG, MONTH_FORMAT)

if USE_TAGGING and 'tagging' in settings.INSTALLED_APPS:
    import tagging
    from tagging.fields import TagField
    HAS_TAGGING = True
else:
    HAS_TAGGING = False

if USE_CATEGORIES and 'categories' in settings.INSTALLED_APPS:
    from categories.models import Category
    HAS_CATEGORIES = True
    category_field = models.ForeignKey(
        Category,
        related_name='viewpoint_categories',
        blank=True,
        null=True)
else:
    HAS_CATEGORIES = False
    category_field = models.IntegerField(blank=True, null=True)

AUTHOR_LIMIT_CHOICES = {}

if STAFF_ONLY and not 'staff' in settings.INSTALLED_APPS:
    AUTHOR_LIMIT_CHOICES = {'is_staff': True}

IMAGE_STORAGE = get_storage_class(DEFAULT_STORAGE)

AUTHOR_MODEL = get_model(*AUTHOR_MODEL.split('.'))

class BlogManager(models.Manager):
    """
    Manager for Blogs that allow you to select just the blogs that are public.
    """
    def published(self, **kwargs):
        """
        Show only the blogs that are public.
        """
        kwargs.update(public=True)
        return self.filter(**kwargs)

    
class Blog(models.Model):
    """
    A Collection of writings by a user or set of users
    """
    title = models.CharField(_("Title"), max_length=255)
    slug = models.SlugField(_("Slug"), unique=True)
    tease = models.TextField(_("Tease"), blank=True)
    
    photo = models.FileField(
        _("Photo"),
        null=True,
        blank=True,
        storage=IMAGE_STORAGE(),
        upload_to='viewpoint/blog/%Y/%m/%d/')
    photo_width = models.IntegerField(blank=True, null=True)
    photo_height = models.IntegerField(blank=True, null=True)

    owners = models.ManyToManyField(
        AUTHOR_MODEL, 
        blank=True, 
        limit_choices_to=AUTHOR_LIMIT_CHOICES,
        verbose_name=_("Owners"))
    
    public = models.BooleanField(_("Public"), default=False,
        help_text=_("Idenifties this blog as being publically accessable."))
    active = models.BooleanField(_("Active"), default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    category = category_field
    alternate_title = models.CharField(
        _("Alternate Title"),
        blank=True,
        default="",
        max_length=100,
        help_text="An alternative title to use on pages with this category."
    )
    description = models.TextField(_("Description"), blank=True, null=True)
    meta_keywords = models.CharField(
        _("Meta Keywords"),
        blank=True,
        null=True,
        default="",
        max_length=255,
        help_text="Comma-separated keywords for search engines.")
    meta_extra = models.TextField(
        _("Meta Extra"),
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

        # If the blog changes its public field, set all
        # entries to the same.
        self.entry_set.all().update(public=self.public)

        if self.photo:
            width, height = get_image_dimensions(self.photo.file, close=True)
        else:
            width, height = None, None
        
        self.photo_width = width
        self.photo_height = height
        
        super(Blog, self).save(*args, **kwargs)
    
    @models.permalink
    def get_absolute_url(self):
        """
        Return the url for this blog
        """
        if DEFAULT_BLOG:
            return ('viewpoint_blog_detail', None, None)
        else:
            return ('viewpoint_blog_detail', None, {'blog_slug': self.slug})
    
    @property
    def owners_list(self):
        """
        Print out the owners in a nice list
        """
        owner_list = [unicode(o) for o in self.owners.all()]
        
        if len(owner_list) > 1:
            return "%s and %s" % (", ".join(owner_list[:-1]), owner_list[-1])
        elif owner_list:
            return owner_list[0]
        else:
            return ''
        
    class Meta:
        ordering = ('title',)
        get_latest_by = 'creation_date'


class EntryManager(models.Manager):
    """
    Manager for Entries that allow you to select just the published entries.
    """
    def published(self, **kwargs):
        """
        Return the published entries only
        """
        if USE_APPROVAL:
            kwargs.update(approved=True, public=True)
        else:
            kwargs.update(public=True)
        kwargs.update(pub_date__lte=datetime.date.today())
        return self.filter(**kwargs)

    
class Entry(models.Model):
    """
    An Entry for a Blog
    """
    blog = models.ForeignKey(Blog, verbose_name=_("Blog"))
    title = models.CharField(_("Title"), max_length=255)
    slug = models.SlugField(_("Slug"), unique_for_date='pub_date')
    author = models.ForeignKey(AUTHOR_MODEL, verbose_name=_("Author"))
    credit = models.CharField(
        _("Credit"),
        max_length=255, 
        blank=True, 
        null=True)
    
    photo = models.FileField(
        _("Photo"),
        null=True,
        blank=True,
        storage=IMAGE_STORAGE(),
        upload_to='viewpoint/entry/%Y/%m/%d/')
    photo_width = models.IntegerField(blank=True, null=True)
    photo_height = models.IntegerField(blank=True, null=True)

    tease = models.TextField(_("Tease"))
    body = models.TextField(_("Body"))
    
    public = models.BooleanField(_("Public"), default=True)
    approved = models.BooleanField(_("Approved"), default=not USE_APPROVAL)
    pub_date = models.DateField(_("Publication Date"), auto_now_add=True)
    pub_time = models.TimeField(_("Publication Time"), auto_now_add=True)
    update_date = models.DateTimeField(_("Update Date"), auto_now=True)
    
    if HAS_CATEGORIES:
        category = models.ForeignKey(
            Category,
            related_name='entry_categories',
            blank=True,
            null=True)
    if HAS_TAGGING:
        tags = TagField(blank=True, null=True)
    objects = EntryManager()
    
    class Meta:
        unique_together = ('blog', 'pub_date', 'slug')
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
        
        if self.photo:
            width, height = get_image_dimensions(self.photo.file, close=True)
        else:
            width, height = None, None
        
        self.photo_width = width
        self.photo_height = height
        
        self.update_date = datetime.datetime.now()
        super(Entry, self).save(*a, **kw)

    @models.permalink
    def get_absolute_url(self):
        """
        Return the url to the blog entry. URL depends whether or not the
        default blog is specified.
        """
        if DEFAULT_BLOG:
            kwargs = {
                'year': self.pub_date.year,
                'month': self.pub_date.strftime(MONTH_FORMAT).lower(),
                'day': self.pub_date.day,
                'slug': self.slug
            }
        else:
            kwargs = {
                'blog_slug': self.blog.slug,
                'year': self.pub_date.year,
                'month': self.pub_date.strftime(MONTH_FORMAT).lower(),
                'day': self.pub_date.day,
                'slug': self.slug
            }
        return ('viewpoint_entry_detail', None, kwargs)
    
    @property
    def paragraphs(self):
        from BeautifulSoup import BeautifulSoup, Tag
        text = "<html><head></head><body>" + self.body + "</body></html>"
        soup = BeautifulSoup(text)
        return [i for i in soup.body.childGenerator() if isinstance(i, Tag)]
    
    if ENTRY_RELATION_MODELS:
        def get_related_content_type(self, content_type):
            return self.entryrelation_set.filter(content_type__name=content_type)
        
        def get_relation_type(self, relation_type):
            return self.entryrelation_set.filter(relation_type=relation_type)
    
if HAS_TAGGING:
    tagging.register(Blog)

RELATIONS = [Q(app_label=al, model=m) for al, m in [x.split('.') for x in ENTRY_RELATION_MODELS]]

ENTRY_RELATION_LIMITS = RELATIONS and reduce(lambda x, y: x|y, RELATIONS)
class EntryRelation(models.Model):
    """Related entry item"""
    entry = models.ForeignKey(Entry)
    content_type = models.ForeignKey(
        ContentType, 
        limit_choices_to=ENTRY_RELATION_LIMITS)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    relation_type = models.CharField(_("Relation Type"), 
        max_length="200", 
        blank=True, 
        null=True,
        help_text=_("A generic text field to tag a relation, like 'leadphoto'."))
        
    def __unicode__(self):
        return u"EntryRelation"

RELATIONS = [Q(app_label=al, model=m) for al, m in [x.split('.') for x in BLOG_RELATION_MODELS]]

BLOG_RELATION_LIMITS = RELATIONS and reduce(lambda x, y: x|y, RELATIONS)
class BlogRelation(models.Model):
    """Related blog item"""
    blog = models.ForeignKey(Blog)
    content_type = models.ForeignKey(
        ContentType, 
        limit_choices_to=BLOG_RELATION_LIMITS)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    relation_type = models.CharField(_("Relation Type"), 
        max_length="200", 
        blank=True, 
        null=True,
        help_text=_("A generic text field to tag a relation, like 'leadphoto'."))
        
    def __unicode__(self):
        return u"BlogRelation"

