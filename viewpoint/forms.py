from django.conf import settings
from django import forms
from models import Blog, Entry

from viewpoint.settings import DEFAULT_BLOG

if 'tinymce' in settings.INSTALLED_APPS:
    from tinymce.widgets import TinyMCE

class EntryForm(forms.ModelForm):
    if 'tinymce' in settings.INSTALLED_APPS:
        body = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    
    class Meta:
        model = Entry
    
    def clean_slug(self):
        if DEFAULT_BLOG:
            self.cleaned_data['blog'] = Blog.objects.get(slug=DEFAULT_BLOG)
        if 'pub_date' in self.cleaned_data:
            pub_date = self.cleaned_data['pub_date']
            try:
                e = Entry.objects.get(slug=self.cleaned_data['slug'],
                                      pub_date__year=pub_date.year,
                                      pub_date__month=pub_date.month,
                                      pub_date__day=pub_date.day)
                if e.id != self.instance.id:
                    raise forms.ValidationError(u"Please enter a different slug. The one you entered is already being used for %s" % pub_date.strftime("%Y-%m-%d"))
                else:
                    return self.cleaned_data['slug']
            except Entry.DoesNotExist:
                pass
            else:
                raise forms.ValidationError(u"Please enter a different slug. The one you entered is already being used for %s" % pub_date.strftime("%Y-%m-%d"))
        return self.cleaned_data['slug']
    
class BlogForm(forms.ModelForm):
    if 'tinymce' in settings.INSTALLED_APPS:
        description = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    
    class Meta:
        model = Blog
