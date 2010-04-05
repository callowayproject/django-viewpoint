from django.test import TestCase
from django.contrib.auth.models import User
from django.template import Template, Context

from categories.models import Category
from models import Blog, Entry

def render(t):
    return Template(t).render(Context())
    
class BlogTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='bloguser')
        self.category = Category.objects.create(slug='blog_category')
        self.blog = Blog.objects.create(
            slug = 'test_blog',
            public = 1,
            owner = self.user,
            category = self.category,
        )
        self.entry = Entry.objects.create(
            public = 1,
            approved = 1,
            blog = self.blog,
            author = self.user,
            category = self.category,
        )
    
    def test_blog_tags(self):
        self.assertEqual('1',render('{% get_blogs blog_category as blogs %}{{ blogs|length }}'))
        self.assertEqual('1',render('{% get_blogs as blogs %}{{ blogs|length }}'))
    
    def test_entry_tags(self):
        self.assertEqual('1',render('{% get_entries as entries %}{{ entries|length }}'))
        self.assertEqual('1',render('{% get_entries test_blog as entries %}{{ entries|length }}'))
        self.assertEqual('1',render('{% get_entries test_blog blog_category as entries %}{{ entries|length }}'))
        
