from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

ROOT_PREFIX = getattr(settings, 'MEDIA_ROOT_PREFIX', settings.MEDIA_ROOT)
URL_PREFIX = getattr(settings, 'MEDIA_URL_PREFIX', settings.MEDIA_URL)

DEFAULT_ROOT = os.path.join(ROOT_PREFIX, 'assets')
DEFAULT_URL = '%smedia/' % URL_PREFIX

class MediaStorage(FileSystemStorage):
    def __init__(self, location='', base_url='', *args, **kwargs):
        real_location = os.path.join(DEFAULT_ROOT, location)
        real_base_url = "%s%s" % (DEFAULT_URL, base_url)
        super(MediaStorage, self).__init__(real_location, real_base_url, *args, **kwargs)
