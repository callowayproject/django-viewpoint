from django.contrib import admin
from django.db.models import get_model
from django.utils.formats import date_format, time_format

from viewpoint.settings import (USE_APPROVAL, AUTHOR_MODEL, 
                                BLOG_RELATION_MODELS, ENTRY_RELATION_MODELS)
from models import Blog, Entry, HAS_CATEGORIES, HAS_TAGGING
from forms import BlogForm, EntryForm

AuthorModel = get_model(*AUTHOR_MODEL.split('.'))

if BLOG_RELATION_MODELS or ENTRY_RELATION_MODELS:
    from genericcollections import GenericCollectionTabularInline

if BLOG_RELATION_MODELS:
    from models import BlogRelation
    
    class InlineBlogRelation(GenericCollectionTabularInline):
        model = BlogRelation

class BlogAdmin(admin.ModelAdmin):
    form = BlogForm
    prepopulated_fields = {"slug": ("title",)}
    list_display = ('title', 'public', 'active', 'entry_count',)
    list_filter = ('public', 'active',)
    list_editable = ('public', 'active',)
    search_fields = ('title', 'tease',)
    related_search_fields = {
        'owner': ('^user__username', '^first_name', '^last_name'),
    }
    filter_horizontal = ('owners', )
    fieldsets = (
        (None, {
            'fields': ('title', 'tease', 'photo'),
        }),
        ('Ownership and Viewing', {
            'fields': ('public', 'active', 'owners'),
        }),
        ('Meta Data', {
            'fields': ('alternate_title', 'description', 'meta_keywords', 'meta_extra'),
            'classes': ('collapse',),
        }),
        ('Advanced', {
            'fields': ('slug',),
            'classes': ('collapse',),
        }),
    )
    if HAS_CATEGORIES:
        fieldsets[-1][1]['fields'] += ('category',)
    
    if BLOG_RELATION_MODELS:
        inlines = (InlineBlogRelation,)
        
        class Media:
            js = ("js/genericcollections.js",)
    
    
    def entry_count(self, obj):
        """Return a count of entries and a link to view them"""
        count = obj.entry_set.count()
        if count == 1:
            item = '%d entry <a href="../entry/?blog__id__exact=%s">View</a>' % (count, obj.id)
        else:
            item = '%d entries <a href="../entry/?blog__id__exact=%s">View</a>' % (count, obj.id)
        return item
    entry_count.allow_tags = True
    actions = ['make_public', 'make_not_public']
    
    def make_public(self, request, queryset):
        rows_updated = queryset.update(public=True)
        if rows_updated == 1:
            message_bit = "1 blog was"
        else:
            message_bit = "%s blogs were" % rows_updated
        self.message_user(request, "%s successfully marked as PUBLIC." % message_bit)
    make_public.short_description = "Mark selected blogs as PUBLIC"

    def make_not_public(self, request, queryset):
        rows_updated = queryset.update(public=False)
        if rows_updated == 1:
            message_bit = "1 blog was"
        else:
            message_bit = "%s blogs were" % rows_updated
        self.message_user(request, "%s successfully marked as NOT PUBLIC." % message_bit)
    make_not_public.short_description = "Mark selected blogs as NOT PUBLIC"
    
    def queryset(self, request):
        qs = super(BlogAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            if AuthorModel.__name__ == "StaffMember":
                return Blog.objects.filter(
                    owners__in=AuthorModel.objects.filter(
                        user__pk=request.user.pk))
            return Blog.objects.filter(owners__in=[request.user,])
        return []


if ENTRY_RELATION_MODELS:
    from models import EntryRelation
    
    class InlineEntryRelation(GenericCollectionTabularInline):
        model = EntryRelation

if USE_APPROVAL:
    PUBLIC_FIELDS = ('public', 'approved', )
else:
    PUBLIC_FIELDS = ('public',)

EXTRA_FIELDS = ()

if HAS_CATEGORIES:
    EXTRA_FIELDS += ('category',)

if HAS_TAGGING:
    EXTRA_FIELDS += ('tags',)

class EntryAdmin(admin.ModelAdmin):
    form = EntryForm
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = 'pub_date'
    related_search_fields = {
        'author': ('^user__username', '^first_name', '^last_name'),
    }
    actions = ['make_approved', 'make_not_approved', 'make_public', 'make_not_public']
    search_fields = ('blog__title', 'title', 'tease', 'body')
    fieldsets = (
        (None, {'fields': (PUBLIC_FIELDS, )}),
        ('Content', {'fields': ('blog', 'title', 'author', 'tease', 'body', ) + EXTRA_FIELDS}),
        ('Media', {'fields': ('photo', 'credit', )}),
        ('Advanced Options', {
            'classes': ('collapse',),
            'fields': ('slug', ),
        }),
    
    )
    list_filter = ('blog',) + PUBLIC_FIELDS
    list_editable = PUBLIC_FIELDS
    list_display = ('title', 'pub_date', 'last_updated', 'blog', ) + PUBLIC_FIELDS
    
    if ENTRY_RELATION_MODELS:
        inlines = (InlineEntryRelation,)
        
        class Media:
            js = ("js/genericcollections.js",)
    
    def last_updated(self, obj):
        """
        Return a formatted pub_date
        """
        return "%s %s" % (date_format(obj.update_date), time_format(obj.update_date))
    last_updated.admin_order_field = 'update_date'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if db_field.name == "author":
                if AuthorModel.__name__ == "StaffMember":
                    kwargs["queryset"] = AuthorModel.objects.filter(user__pk=request.user.pk)
                else:
                    from django.contrib.auth.models import User
                    kwargs["queryset"] = User.objects.filter(pk=request.user.pk)
                return db_field.formfield(**kwargs)
            elif db_field.name == "blog":
                if AuthorModel.__name__ == "StaffMember":
                    kwargs["queryset"] = Blog.objects.filter(
                        owners__in=AuthorModel.objects.filter(
                            user__pk=request.user.pk))
                else:
                    kwargs["queryset"] = Blog.objects.filter(owners__in=[request.user,])
                return db_field.formfield(**kwargs)
        return super(EntryAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
    
    def make_approved(self, request, queryset):
        rows_updated = queryset.update(approved=True)
        if rows_updated == 1:
            message_bit = "One entry was"
        else:
            message_bit = "%s entries were" % rows_updated
        self.message_user(request, "%s successfully marked as APPROVED." % message_bit)
    make_approved.short_description = "Mark selected entries as APPROVED"

    def make_not_approved(self, request, queryset):
        rows_updated = queryset.update(approved=False)
        if rows_updated == 1:
            message_bit = "1 entry was"
        else:
            message_bit = "%s entries were" % rows_updated
        self.message_user(request, "%s successfully marked as NOT APPROVED." % message_bit)
    make_not_approved.short_description = "Mark selected entries as NOT APPROVED"

    def make_public(self, request, queryset):
        rows_updated = queryset.update(public=True)
        if rows_updated == 1:
            message_bit = "1 entry was"
        else:
            message_bit = "%s entries were" % rows_updated
        self.message_user(request, "%s successfully marked as PUBLIC." % message_bit)
    make_public.short_description = "Mark selected entries as PUBLIC"

    def make_not_public(self, request, queryset):
        rows_updated = queryset.update(public=False)
        if rows_updated == 1:
            message_bit = "1 entry was"
        else:
            message_bit = "%s entries were" % rows_updated
        self.message_user(request, "%s successfully marked as NOT PUBLIC." % message_bit)
    make_not_public.short_description = "Mark selected entries as NOT PUBLIC"
    
    def queryset(self, request):
        from django.db.models import Q
        
        qs = super(EntryAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            if AuthorModel.__name__ == "StaffMember":
                blog_ids = Blog.objects.filter(
                    owners__in=AuthorModel.objects.filter(
                        user__pk=request.user.pk)).values_list('pk', flat=True)
                author_pk = AuthorModel.objects.filter(user__pk=request.user.pk)
            else:
                blog_ids = Blog.objects.filter(
                    owners__in=[request.user.pk,]).values_list('pk', flat=True)
                author_pk = request.user.pk
            return qs.filter(Q(blog__id__in=blog_ids) | Q(author__pk=author_pk))
    
    # def save_model(self, request, obj, form, change):
    #     obj.author = request.user
    #     obj.save()
    
    
admin.site.register(Blog, BlogAdmin)
admin.site.register(Entry, EntryAdmin)
