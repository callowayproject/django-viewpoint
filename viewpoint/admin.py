from models import Blog, Entry
from forms import BlogForm, EntryForm
from django.contrib import admin
from autocomplete.admin import AutoCompleteAdmin
from django.conf import settings

class BlogAdmin(AutoCompleteAdmin):
    form = BlogForm
    prepopulated_fields = {"slug": ("title",)}
    related_search_fields = {
        'owner': ('^user__username', '^first_name', '^last_name'),
    }
    
    def queryset(self, request):
        qs = super(BlogAdmin, self).queryset(request)
        from profiles import get_profile
        profile = get_profile(request.user)
        if request.user.is_superuser:
            return qs
        elif profile.is_mayor:
            return qs.filter(category__in=profile.categories.all())
        return []
    

if hasattr(settings, 'ENTRY_RELATION_MODELS'):
    from genericcollections import *
    from models import EntryRelation
    
    class InlineEntryRelation(GenericCollectionTabularInline):
        model = EntryRelation


class EntryAdmin(AutoCompleteAdmin):
    form = EntryForm
    prepopulated_fields = {"slug": ("title",)}
    exclude = ['approved', 'public']
    list_display = ('title', 'pub_date','blog', 'public', 'approved')
    related_search_fields = {
        'author': ('^user__username', '^first_name', '^last_name'),
    }
    actions = ['make_approved', 'make_not_approved', 'make_public', 'make_not_public']
    search_fields = ('blog__title','title','tease','body')   
    list_filter = ('blog',)
    
    if hasattr(settings, 'ENTRY_RELATION_MODELS'):
        inlines = (InlineEntryRelation,)
    
    def make_approved(self, request, queryset):
        rows_updated = queryset.update(approved=True)
        if rows_updated == 1:
            message_bit = "1 entry was"
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
        from profiles import get_profile
        profile = get_profile(request.user)
        if request.user.is_superuser:
            return qs
        elif profile.is_mayor:
            return qs.filter(blog__category__in=profile.categories.all())
        else:
            return qs.filter(author__pk=request.user.pk)
    
    # def save_model(self, request, obj, form, change):
    #     obj.author = request.user
    #     obj.save()
    
    
admin.site.register(Blog, BlogAdmin)
admin.site.register(Entry, EntryAdmin)