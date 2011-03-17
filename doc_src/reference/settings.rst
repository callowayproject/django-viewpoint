
========
Settings
========

**New in version 0.8:** Settings have been refactored to mimic the current trend of having a dictionary of settings. The old settings will still work, but a Deprecation warning will be raised.

VIEWPOINT_SETTINGS
==================

``VIEWPOINT_SETTINGS`` is a dictionary of individual settings. You only need to include the individual settings that you wish to override from the defaults.

The default settings are:

.. code-block:: python

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
	    'URL_REGEXES': {
	        'blog': r'^(?P<blog_slug>[-\w]+)/$',
	        'year': r'^(?P<blog_slug>[-\w]+)/(?P<year>\d{4})/$',
	        'month': r'^(?P<blog_slug>[-\w]+)/(?P<year>\d{4})/(?P<month>%b)/$',
	        'day': r'^(?P<blog_slug>[-\w]+)/(?P<year>\d{4})/(?P<month>%b)/(?P<day>\d{1,2})/$',
	        'entry': r'^(?P<blog_slug>[-\w]+)/(?P<year>\d{4})/(?P<month>%b)/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
	    }
	}

STAFF_ONLY
==========

Should only users marked as "is_staff" are allowed to post to a blog. The owners list is narrowed down to only these users if true.

**Default:** ``True``

ENTRY_RELATION_MODELS
=====================

A list of strings in ``'app.Model'`` format. Authors can relate any instance of these models to any blog entry. For example: to show related blog entries you would set it to ``['viewpoint.Entry',]``\ .

**Default:** ``[]``

BLOG_RELATION_MODELS
====================

A list of strings in ``'app.Model'`` format. Authors can relate any instance of these models to any blog. For example: to show related blogs you would set it to ``['viewpoint.Blog',]``\ .

**Default:** ``[]``

USE_APPROVAL
============

Require moderators to approve entries before publication.

**Default:** ``False``

DEFAULT_STORAGE
===============

The default file storage for photos for entries and blogs.

**Default:** ``settings.DEFAULT_FILE_STORAGE``

USE_CATEGORIES
==============

Include support for django-categories.

**Default:** ``False``

AUTHOR_MODEL
============

A string in the format ``'app.Model'`` to use as the basis for the authors of blog entries.

**Default:** ``'auth.user'``

USE_TAGGING
===========

Include support for django-tagging.

**Default:** ``False``

.. _DEFAULT_BLOG:

DEFAULT_BLOG
============

If you aren't going to use multiple blogs, this is the name of the one blog you are going to use. URLs are refactored to hide the name of the blog.

**Default:** ``''``


.. _MONTH_FORMAT:

MONTH_FORMAT
============

For your URLs, you can customize the format of the month in the default URL regular expressions.


.. table:: Month formatting codes

   ======  =================================  =========
   Code    Description                        Example
   ======  =================================  =========
   ``%b``  Locale’s abbreviated month name    Dec
   ``%B``  Locale's full month name           December
   ``%m``  Month as a decimal number [01,12]  12
   ======  =================================  =========

**Default:** ``r'%b'``

URL_REGEXES
===========

A dictionary of regular expressions to use for matching URLs. The dictionary should have ``'blog'``\ , ``'year'``\ , ``'month'``\ , ``'day'``\ , ``'entry'``\ keys. The default URL_REGEXES use the :ref:`MONTH_FORMAT`\ .

**Default:**
If the :ref:`DEFAULT_BLOG` is set:

.. code-block:: python

	VIEWPOINT_SETTINGS['URL_REGEXES'] = {
	    'blog': r'^$',
	    'year': r'^(?P<year>\d{4})/$',
	    'month': r'^(?P<year>\d{4})/(?P<month>%b)/$',
	    'day': r'^(?P<year>\d{4})/(?P<month>%b)/(?P<day>\d{1,2})/$',
	    'entry': r'^(?P<year>\d{4})/(?P<month>%b)/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$'
	}


If the :ref:`DEFAULT_BLOG` is not set:

.. code-block:: python

	VIEWPOINT_SETTINGS['URL_REGEXES'] = {
	    'blog': r'^(?P<blog_slug>[-\w]+)/$',
	    'year': r'^(?P<blog_slug>[-\w]+)/(?P<year>\d{4})/$',
	    'month': r'^(?P<blog_slug>[-\w]+)/(?P<year>\d{4})/(?P<month>%b)/$',
	    'day': r'^(?P<blog_slug>[-\w]+)/(?P<year>\d{4})/(?P<month>%b)/(?P<day>\d{1,2})/$',
	    'entry': r'^(?P<blog_slug>[-\w]+)/(?P<year>\d{4})/(?P<month>%b)/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$'
	}
