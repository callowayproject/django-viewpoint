from models import Blog, Entry
from django.contrib.contenttypes.models import ContentType
from django.contrib.comments.models import Comment
from django.db import connection

from categories.models import Category
from staff.models import StaffMember 


def get_blogs(category=None):
    lookup = {}
    if isinstance(category, Category):
        lookup['category'] = category
    elif category:
        lookup['category'] = Category.objects.get(slug=category)
    return Blog.objects.published(**lookup)
get_blogs.function = 1    
    
def get_entries(blog=None, category=None, limit=None):
    lookup = {}
    if isinstance(category, Category):
        lookup['category'] = category
    elif category:
        lookup['category'] = Category.objects.get(slug=category)
    if isinstance(blog, Blog):
        lookup['blog'] = blog
    elif blog:
        lookup['blog'] = Blog.objects.get(slug=blog)        
    entries = Entry.objects.published(**lookup).order_by('-pub_date','-pub_time')
    if not limit is None:
        return entries[:int(limit)]
    return entries
get_entries.function = 1    
    
  
def get_comment_count(entry):
    return Comment.objects.filter(
        content_type = ContentType.objects.get_for_model(Entry),
        object_pk = str(entry.pk)
    ).count() - 1
get_comment_count.function = 1

def get_most_commented_entries(blog=None, category=None):
    ctype = ContentType.objects.get_for_model(Entry)
    c = connection.cursor()
    c.execute("""SELECT COUNT(*), "django_comments"."content_type_id", "django_comments"."object_pk", MAX("django_comments"."content_type_id") as "content_type_id" 
                            FROM "django_comments" 
                            WHERE  "django_comments"."content_type_id" = %s
                            AND "django_comments"."submit_date" >= NOW() - interval '3 days'
                            AND "django_comments"."is_public" = true
                            GROUP BY "django_comments"."content_type_id", "django_comments"."object_pk"
                            ORDER BY COUNT(*) DESC
                            LIMIT 10""" % ctype.id)
    lookup = {}
    if isinstance(category, Category):
        lookup['category'] = category
    elif category:
        lookup['category'] = Category.objects.get(slug=category)
    if isinstance(blog, Blog):
        lookup['blog'] = blog
    elif blog:
        lookup['blog'] = Blog.objects.get(slug=blog)  
    allowed = Entry.objects.published(**lookup)
    entries = []
    for row in c.fetchall():
        try:
            entry = Entry.objects.get(pk=row[2])
        except Entry.DoesNotExist:
            continue
        if entry in allowed:
            entries.append(entry)
    return entries
get_most_commented_entries.function = 1
