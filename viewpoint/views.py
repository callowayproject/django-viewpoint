from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Q
from django.template.loader import select_template
from viewpoint.settings import DEFAULT_BLOG, MONTH_FORMAT
from django.views.generic.date_based import archive_day, archive_month, \
                                            archive_year, archive_today, \
                                            archive_week, object_detail

from models import Blog, Entry

def get_template(blog_slug, template_name):
    """
    Given a blog slug and template name (without the .html), this will return
    the appropriate template, looking in various directories.
    """
    return select_template((
            'viewpoint/%s/%s.html' % (blog_slug, template_name), 
            'viewpoint/%s.html' % template_name
        )).name

def generic_blog_entry_view(request, *args,  **kwargs):
    """
    A generic override for the default Django generic views 
    """
    blog_slug = kwargs.pop('blog_slug', DEFAULT_BLOG)
    queryset = Entry.objects.published(blog__slug=blog_slug)
    params = {
        'queryset': queryset,
        'date_field': 'pub_date',
        'allow_empty': True,
    }
    params.update(kwargs)
    print ''
    if 'slug' in kwargs.keys():
        if 'template_name' not in params.keys():
            params['template_name'] = get_template(blog_slug, 'entry_detail')
            params['month_format'] = MONTH_FORMAT
            params.pop('allow_empty')
        return object_detail(request, **params)
    elif 'day' in kwargs.keys():
        if 'template_name' not in params.keys():
            params['template_name'] = get_template(blog_slug, 'entry_archive_day')
            params['month_format'] = MONTH_FORMAT
        return archive_day(request, **params)
    elif 'month' in kwargs.keys():
        if 'template_name' not in params.keys():
            params['template_name'] = get_template(blog_slug, 'entry_archive_month')
            params['month_format'] = MONTH_FORMAT
        return archive_month(request, **params)
    elif 'week' in kwargs.keys():
        if 'template_name' not in params.keys():
            params['template_name'] = get_template(blog_slug, 'entry_archive_week')
        return archive_week(request, **params)
    elif 'year' in kwargs.keys():
        if 'template_name' not in params.keys():
            params['template_name'] = get_template(blog_slug, 'entry_archive_year')
        return archive_year(request, **params)
    else:
        if 'template_name' not in params.keys():
            params['template_name'] = get_template(blog_slug, 'entry_archive_today')
        return archive_today(request, **params)


def blog_detail(request, blog_slug=DEFAULT_BLOG):
    """
    Return the blog_detail page for the specified blog.
    """
    blog = get_object_or_404(Blog, slug=blog_slug, public=True)
    return render_to_response(get_template(blog_slug, 'blog_detail'), {
            'object':blog,
        }, context_instance=RequestContext(request))

# Stop Words courtesy of 
# http://www.dcs.gla.ac.uk/idom/ir_resources/linguistic_utils/stop_words
STOP_WORDS = r"""\b(a|about|above|across|after|afterwards|again|against|all|
almost|alone|along|already|also|although|always|am|among|amongst|amoungst|
amount|an|and|another|any|anyhow|anyone|anything|anyway|anywhere|are|around|
as|at|back|be|became|because|become|becomes|becoming|been|before|beforehand|
behind|being|below|beside|besides|between|beyond|bill|both|bottom|but|by|call|
can|cannot|cant|co|computer|con|could|couldnt|cry|de|describe|detail|do|done|
down|due|during|each|eg|eight|either|eleven|else|elsewhere|empty|enough|etc|
even|ever|every|everyone|everything|everywhere|except|few|fifteen|fify|fill|
find|fire|first|five|for|former|formerly|forty|found|four|from|front|full|
further|get|give|go|had|has|hasnt|have|he|hence|her|here|hereafter|hereby|
herein|hereupon|hers|herself|him|himself|his|how|however|hundred|i|ie|if|in|
inc|indeed|interest|into|is|it|its|itself|keep|last|latter|latterly|least|
less|ltd|made|many|may|me|meanwhile|might|mill|mine|more|moreover|most|mostly|
move|much|must|my|myself|name|namely|neither|never|nevertheless|next|nine|no|
nobody|none|noone|nor|not|nothing|now|nowhere|of|off|often|on|once|one|only|
onto|or|other|others|otherwise|our|ours|ourselves|out|over|own|part|per|
perhaps|please|put|rather|re|same|see|seem|seemed|seeming|seems|serious|
several|she|should|show|side|since|sincere|six|sixty|so|some|somehow|someone|
something|sometime|sometimes|somewhere|still|such|system|take|ten|than|that|
the|their|them|themselves|then|thence|there|thereafter|thereby|therefore|
therein|thereupon|these|they|thick|thin|third|this|those|though|three|through|
throughout|thru|thus|to|together|too|top|toward|towards|twelve|twenty|two|un|
under|until|up|upon|us|very|via|was|we|well|were|what|whatever|when|whence|
whenever|where|whereafter|whereas|whereby|wherein|whereupon|wherever|whether|
which|while|whither|who|whoever|whole|whom|whose|why|will|with|within|without|
would|yet|you|your|yours|yourself|yourselves)\b"""


def search(request, template_name='blog/entry_search.html'):
    """
    Search for blog posts.

    This template will allow you to setup a simple search form that will try 
    to return results based on given search strings. The queries will be put 
    through a stop words filter to remove words like 'the', 'a', or 'have' to 
    help imporve the result set.

    Template: ``blog/post_search.html``
    Context:
        object_list
            List of blog posts that match given search term(s).
        search_term
            Given search term.
    """
    import re
    context = {}
    if request.GET:
        stop_word_list = re.compile(STOP_WORDS, re.IGNORECASE)
        search_term = str(request.GET['q'])
        cleaned_search_term = stop_word_list.sub('', search_term).strip()
        if len(cleaned_search_term) > 1:
            post_list = Entry.objects.published().filter(Q(body__icontains=cleaned_search_term) | Q(tags__icontains=cleaned_search_term) | Q(categories__title__icontains=cleaned_search_term))
            context = {'object_list': post_list, 'search_term':search_term}
        else:
            message = 'Search term was too vague. Please try again.'
            context = {'message':message}
    return render_to_response(template_name, context, context_instance=RequestContext(request))
 
 
def feeds_index(request, template_name='blog/feeds_index.html'):
    blogs = Blog.objects.filter(public=True).order_by('title')
    return render_to_response(template_name,
                              {'blogs': blogs},
                              context_instance=RequestContext(request))
    
