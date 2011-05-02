import warnings

from django.conf import settings

VIEWPOINT_SETTINGS = {
    'STAFF_ONLY': True,
    'ENTRY_RELATION_MODELS': [],
    'BLOG_RELATION_MODELS': [],
    'USE_APPROVAL': False,
    'DEFAULT_STORAGE': settings.DEFAULT_FILE_STORAGE,
    'AUTHOR_MODEL': 'auth.User',
    'USE_CATEGORIES': False,
    'USE_TAGGING': False,
    'DEFAULT_BLOG': '',
    'MONTH_FORMAT': r"%b",
    'URL_REGEXES': {},
}

VIEWPOINT_SETTINGS.update(getattr(settings, 'VIEWPOINT_SETTINGS', {}))

if hasattr(settings, 'VIEWPOINT_STAFF_ONLY'):
    warnings.warn(
        "settings.VIEWPOINT_STAFF_ONLY is deprecated; use settings.VIEWPOINT_SETTINGS instead.",
        DeprecationWarning
    )
    STAFF_ONLY = getattr(settings, 'VIEWPOINT_STAFF_ONLY')
else:
    STAFF_ONLY = VIEWPOINT_SETTINGS['STAFF_ONLY']

if hasattr(settings, 'ENTRY_RELATION_MODELS'):
    warnings.warn(
        "settings.ENTRY_RELATION_MODELS is deprecated; use settings.VIEWPOINT_SETTINGS instead.",
        DeprecationWarning
    )
    ENTRY_RELATION_MODELS = getattr(settings, 'ENTRY_RELATION_MODELS', [])
else:
    ENTRY_RELATION_MODELS = VIEWPOINT_SETTINGS['ENTRY_RELATION_MODELS']

if hasattr(settings, 'BLOG_RELATION_MODELS'):
    warnings.warn(
        "settings.BLOG_RELATION_MODELS is deprecated; use settings.VIEWPOINT_SETTINGS instead.",
        DeprecationWarning
    )
    BLOG_RELATION_MODELS = getattr(settings, 'BLOG_RELATION_MODELS')
else:
    BLOG_RELATION_MODELS = VIEWPOINT_SETTINGS['BLOG_RELATION_MODELS']

if hasattr(settings, 'VIEWPOINT_USE_APPROVAL'):
    warnings.warn(
        "settings.VIEWPOINT_USE_APPROVAL is deprecated; use settings.VIEWPOINT_SETTINGS instead.",
        DeprecationWarning
    )
    USE_APPROVAL = getattr(settings, 'VIEWPOINT_USE_APPROVAL')
else:
    USE_APPROVAL = VIEWPOINT_SETTINGS['USE_APPROVAL']

if hasattr(settings, 'VIEWPOINT_DEFAULT_STORAGE'):
    warnings.warn(
        "settings.VIEWPOINT_DEFAULT_STORAGE is deprecated; use settings.VIEWPOINT_SETTINGS instead.",
        DeprecationWarning
    )
    DEFAULT_STORAGE = getattr(settings, 'VIEWPOINT_DEFAULT_STORAGE')
else:
    DEFAULT_STORAGE = VIEWPOINT_SETTINGS['DEFAULT_STORAGE']

if hasattr(settings, 'VIEWPOINT_USE_CATEGORIES'):
    warnings.warn(
        "settings.VIEWPOINT_USE_CATEGORIES is deprecated; use settings.VIEWPOINT_SETTINGS instead.",
        DeprecationWarning
    )
    USE_CATEGORIES = getattr(settings, 'VIEWPOINT_USE_CATEGORIES')
else:
    USE_CATEGORIES = VIEWPOINT_SETTINGS['USE_CATEGORIES']

if hasattr(settings, 'VIEWPOINT_AUTHOR_MODEL'):
    warnings.warn(
        "settings.VIEWPOINT_AUTHOR_MODEL is deprecated; use settings.VIEWPOINT_SETTINGS instead.",
        DeprecationWarning
    )
    AUTHOR_MODEL = getattr(settings, 'VIEWPOINT_AUTHOR_MODEL')
else:
    AUTHOR_MODEL = VIEWPOINT_SETTINGS['AUTHOR_MODEL']

if hasattr(settings, 'VIEWPOINT_USE_TAGGING'):
    warnings.warn(
        "settings.VIEWPOINT_USE_TAGGING is deprecated; use settings.VIEWPOINT_SETTINGS instead.",
        DeprecationWarning
    )
    USE_TAGGING = getattr(settings, 'VIEWPOINT_USE_TAGGING')
else:
    USE_TAGGING = VIEWPOINT_SETTINGS['USE_TAGGING']

if hasattr(settings, 'VIEWPOINT_DEFAULT_BLOG'):
    warnings.warn(
        "settings.VIEWPOINT_DEFAULT_BLOG is deprecated; use settings.VIEWPOINT_SETTINGS instead.",
        DeprecationWarning
    )
    DEFAULT_BLOG = getattr(settings, 'VIEWPOINT_DEFAULT_BLOG')
else:
    DEFAULT_BLOG = VIEWPOINT_SETTINGS['DEFAULT_BLOG']

if hasattr(settings, 'VIEWPOINT_MONTH_FORMAT'):
    warnings.warn(
        "settings.VIEWPOINT_MONTH_FORMAT is deprecated; use settings.VIEWPOINT_SETTINGS instead.",
        DeprecationWarning
    )
    MONTH_FORMAT = getattr(settings, 'VIEWPOINT_MONTH_FORMAT', r"%b")
else:
    MONTH_FORMAT = VIEWPOINT_SETTINGS['MONTH_FORMAT']

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

if hasattr(settings, 'VIEWPOINT_URL_REGEXES'):
    warnings.warn(
        "settings.VIEWPOINT_URL_REGEXES is deprecated; use settings.VIEWPOINT_SETTINGS instead.",
        DeprecationWarning
    )
    URL_REGEXES = getattr(settings, 'VIEWPOINT_URL_REGEXES')
else:
    if VIEWPOINT_SETTINGS['URL_REGEXES'] == {}:
        VIEWPOINT_SETTINGS['URL_REGEXES'] = DEFAULT_REGEXES
    URL_REGEXES = VIEWPOINT_SETTINGS['URL_REGEXES']
