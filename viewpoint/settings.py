from django.conf import settings

STAFF_ONLY = getattr(settings, 'VIEWPOINT_STAFF_ONLY', True)

ENTRY_RELATION_MODELS = getattr(settings, 'ENTRY_RELATION_MODELS', [])

BLOG_RELATION_MODELS = getattr(settings, 'BLOG_RELATION_MODELS', [])

USE_APPROVAL = getattr(settings, 'VIEWPOINT_USE_APPROVAL', False)