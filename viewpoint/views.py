from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden, HttpResponse
from django.contrib.auth.decorators import user_passes_test,login_required
from django.db.models import Q
from django.views.decorators.cache import cache_page
from django.views.generic import date_based
from django.template.loader import select_template

from models import Blog,Entry
import time, datetime


def archive_day(request, slug, year, month, day):
    blog = get_object_or_404(Blog, slug=slug, public=True)
    try:
        date = datetime.date(*time.strptime('%s-%s-%s' % (year, month, day), '%Y-%b-%d')[:3])
    except ValueError:
        raise Http404
    return render_to_response('blog/entry_archive.html', {
        'blog': 'blog',
        'entries': Entry.objects.published(blog=blog,pub_date__year=date.year,pub_date__month=date.month,pub_date__day=date.day)
    }, context_instance=RequestContext(request))
    
def archive_month(request, slug, year, month):
    blog = get_object_or_404(Blog, slug=slug, public=True)
    try:
        date = datetime.date(*time.strptime('%s-%s' % (year, month), '%Y-%b')[:3])
    except ValueError:
        raise Http404
    return render_to_response('blog/entry_archive.html', {
        'blog': 'blog',
        'month': month,
        'year': year,
        'entries': Entry.objects.published(blog=blog,pub_date__year=date.year,pub_date__month=date.month)
    }, context_instance=RequestContext(request))
    
def archive_year(request, slug, year):
    blog = get_object_or_404(Blog, slug=slug, public=True)
    try:
        date = datetime.date(*time.strptime(year, '%Y')[:3])
    except ValueError:
        raise Http404
    return render_to_response('blog/entry_archive_year.html', {
        'blog': 'blog',
        'year': year,
        'entries': Entry.objects.published(blog=blog,pub_date__year=date.year)
    }, context_instance=RequestContext(request))

#@cache_page(3600)
def entry_detail(request, blog_slug, year, month, day, slug):
    try:
        date = datetime.date(*time.strptime('%s-%s-%s' % (year, month, day), '%Y-%b-%d')[:3])
    except ValueError:
        raise Http404
    start_date = datetime.datetime.combine(date, datetime.time.min)
    end_date = datetime.datetime.combine(date, datetime.time.max)
    blog = get_object_or_404(Blog, slug=blog_slug)
    entry = get_object_or_404(Entry, pub_date__range=(start_date, end_date), slug=slug, blog=blog)
    if entry.public or entry.author == request.user:
        return render_to_response('blog/entry_detail.html', {'entry':entry}, context_instance=RequestContext(request))
    raise Http404

#@cache_page(3600)
def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug, public=True)
    return render_to_response(select_template([
        'blog/%s.html' % blog.slug,
        'blog/blog_detail.html']), {
            'blog':blog,
            'entries': Entry.objects.published(blog=blog)
        }, context_instance=RequestContext(request))

   # Stop Words courtesy of http://www.dcs.gla.ac.uk/idom/ir_resources/linguistic_utils/stop_words
STOP_WORDS = r"""\b(a|about|above|across|after|afterwards|again|against|all|almost|alone|along|already|also|
although|always|am|among|amongst|amoungst|amount|an|and|another|any|anyhow|anyone|anything|anyway|anywhere|are|
around|as|at|back|be|became|because|become|becomes|becoming|been|before|beforehand|behind|being|below|beside|
besides|between|beyond|bill|both|bottom|but|by|call|can|cannot|cant|co|computer|con|could|couldnt|cry|de|describe|
detail|do|done|down|due|during|each|eg|eight|either|eleven|else|elsewhere|empty|enough|etc|even|ever|every|everyone|
everything|everywhere|except|few|fifteen|fify|fill|find|fire|first|five|for|former|formerly|forty|found|four|from|
front|full|further|get|give|go|had|has|hasnt|have|he|hence|her|here|hereafter|hereby|herein|hereupon|hers|herself|
him|himself|his|how|however|hundred|i|ie|if|in|inc|indeed|interest|into|is|it|its|itself|keep|last|latter|latterly|
least|less|ltd|made|many|may|me|meanwhile|might|mill|mine|more|moreover|most|mostly|move|much|must|my|myself|name|
namely|neither|never|nevertheless|next|nine|no|nobody|none|noone|nor|not|nothing|now|nowhere|of|off|often|on|once|
one|only|onto|or|other|others|otherwise|our|ours|ourselves|out|over|own|part|per|perhaps|please|put|rather|re|same|
see|seem|seemed|seeming|seems|serious|several|she|should|show|side|since|sincere|six|sixty|so|some|somehow|someone|
something|sometime|sometimes|somewhere|still|such|system|take|ten|than|that|the|their|them|themselves|then|thence|
there|thereafter|thereby|therefore|therein|thereupon|these|they|thick|thin|third|this|those|though|three|through|
throughout|thru|thus|to|together|too|top|toward|towards|twelve|twenty|two|un|under|until|up|upon|us|very|via|was|
we|well|were|what|whatever|when|whence|whenever|where|whereafter|whereas|whereby|wherein|whereupon|wherever|whether|
which|while|whither|who|whoever|whole|whom|whose|why|will|with|within|without|would|yet|you|your|yours|yourself|
yourselves)\b"""


def search(request, template_name='blog/entry_search.html'):
    """
    Search for blog posts.

    This template will allow you to setup a simple search form that will try to return results based on
    given search strings. The queries will be put through a stop words filter to remove words like
    'the', 'a', or 'have' to help imporve the result set.

    Template: ``blog/post_search.html``
    Context:
        object_list
            List of blog posts that match given search term(s).
        search_term
            Given search term.
    """
    context = {}
    if request.GET:
        stop_word_list = re.compile(STOP_WORDS, re.IGNORECASE)
        search_term = str(request.GET['q'])
        cleaned_search_term = stop_word_list.sub('', search_term).strip()
        if len(cleaned_search_term) > 1:
            post_list = Post.objects.published().filter(Q(body__icontains=cleaned_search_term) | Q(tags__icontains=cleaned_search_term) | Q(categories__title__icontains=cleaned_search_term))
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
    
