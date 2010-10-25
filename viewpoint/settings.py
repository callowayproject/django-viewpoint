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