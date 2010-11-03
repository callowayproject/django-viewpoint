from django.conf import settings

STAFF_ONLY = getattr(settings, 'VIEWPOINT_STAFF_ONLY', True)

ENTRY_RELATION_MODELS = getattr(settings, 'ENTRY_RELATION_MODELS', [])

BLOG_RELATION_MODELS = getattr(settings, 'BLOG_RELATION_MODELS', [])

USE_APPROVAL = getattr(settings, 'VIEWPOINT_USE_APPROVAL', False)

DEFAULT_STORAGE = getattr(settings, 'VIEWPOINT_DEFAULT_STORAGE', settings.DEFAULT_FILE_STORAGE)

USE_CATEGORIES = getattr(settings, 'VIEWPOINT_USE_CATEGORIES', False)
AUTHOR_MODEL = getattr(settings, 'VIEWPOINT_AUTHOR_MODEL', 'auth.user')
USE_TAGGING = getattr(settings, 'VIEWPOINT_USE_TAGGING', False)

DEFAULT_BLOG = getattr(settings, 'VIEWPOINT_DEFAULT_BLOG', '')
MONTH_FORMAT = getattr(settings, 'VIEWPOINT_MONTH_FORMAT', r"%b")
# DAY_FORMAT = getattr(settings, 'VIEWPOINT_DAY_FORMAT', r"\d{1,2}")

def urlregex_generator(period, month_format=MONTH_FORMAT):
    """
    Return a regex for the period (blog, year, month, day, entry)
    """
    periods = dict(year=1, month=2, day=3, entry=4)
    formats = {
        '%b': r"\w{3}",
        '%B': r"\w+",
        '%m': r"\d{1,2}"
    }
    
    if DEFAULT_BLOG:
        regex = []
        if period == 'blog':
            return '^$'
    else:
        regex = [r'(?P<blog_slug>[-\w]+)',]
        if period == 'blog':
            return r'^(?P<blog_slug>[-\w]+)/$'
    
    path = [
        r'(?P<year>\d{4})', 
        r'(?P<month>%s)' % formats[month_format], 
        r'(?P<day>\d{1,2})', 
        r'(?P<slug>[-\w]+)'
    ]
    regex.extend(path[:periods[period]])
    
    return '^%s/$' % "/".join(regex)

DEFAULT_REGEXES = {}
for item in ('blog', 'year', 'month', 'day', 'entry'):
    DEFAULT_REGEXES[item] = urlregex_generator(item)
URL_REGEXES = getattr(settings, 'VIEWPOINT_URL_REGEXES', DEFAULT_REGEXES)
