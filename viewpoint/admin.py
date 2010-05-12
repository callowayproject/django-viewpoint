from models import Blog, Entry
from forms import BlogForm, EntryForm
from django.contrib import admin
from django.conf import settings

class BlogAdmin(admin.ModelAdmin):
    form = BlogForm
    list_display = ('title', 'public')
    prepopulated_fields = {"slug": ("title",)}
    related_search_fields = {
        'owner': ('^user__username', '^first_name', '^last_name'),
    }
    fieldsets = (
        (None, {
            'fields': ('title', 'tease', 'photo'),
        }),
        ('Ownership and Viewing', {
            'fields': ('public', 'owners'),
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
            return request.user.blog_set.all()
        return []


if hasattr(settings, 'ENTRY_RELATION_MODELS'):
    from genericcollections import *
    from models import EntryRelation
    
    class InlineEntryRelation(GenericCollectionTabularInline):
        model = EntryRelation


class EntryAdmin(admin.ModelAdmin):
    form = EntryForm
    prepopulated_fields = {"slug": ("title",)}
    exclude = ['approved']
    list_display = ('title', 'pub_date','blog', 'public', 'approved')
    related_search_fields = {
        'author': ('^user__username', '^first_name', '^last_name'),
    }
    actions = ['make_approved', 'make_not_approved', 'make_public', 'make_not_public']
    search_fields = ('blog__title','title','tease','body')   
    list_filter = ('blog',)
    raw_id_fields = ('author','blog')
    
    if hasattr(settings, 'ENTRY_RELATION_MODELS'):
        inlines = (InlineEntryRelation,)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if db_field.name == "author":
                from django.contrib.auth.models import User
                kwargs["queryset"] = User.objects.filter(pk=request.user.pk)
                return db_field.formfield(**kwargs)
            elif db_field.name == "blog":
                kwargs["queryset"] = request.user.blog_set.all()
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
        qs = super(EntryAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(author__pk=request.user.pk)
    
    # def save_model(self, request, obj, form, change):
    #     obj.author = request.user
    #     obj.save()
    
    
admin.site.register(Blog, BlogAdmin)
admin.site.register(Entry, EntryAdmin)