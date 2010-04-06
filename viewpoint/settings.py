from django.conf import settings

STAFF_ONLY = getattr(settings, 'VIEWPOINT_STAFF_ONLY', True)

RELATION_MODELS = getattr(settings, 'ENTRY_RELATION_MODELS', [])