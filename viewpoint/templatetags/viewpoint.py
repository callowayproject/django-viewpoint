from django import template
from django.utils.safestring import mark_safe
register = template.Library()

@register.tag('get_related_content_type')
def do_get_related_content_type(parser, token):
    """
    Gets relations to a story based on the content type
    
    {% get_related_content_type item content_type as var_name %}
    
    {% get_related_content_type object Image as photo %}
    """
    try:
        tag_name, obj, content_type, as_txt, var = token.split_contents()
        content_type = content_type.replace("'", '').replace('"', '')
    except ValueError:
        raise template.TemplateSyntaxError("'get_related_content_type' requires an object, content_type and a variable name.")
    return RelatedNode(obj, var, content_type=content_type)

@register.tag('get_relation_type')
def do_get_relation_type(parser, token):
    """
    Gets the relations to a story based on the relation type
    
    {% get_relation_type item relation_type as var_name %}
    
    {% get_relation_type object leadphoto as leadphoto %}
    """
    try:
        tag_name, obj, relation_type, as_txt, var = token.split_contents()
        relation_type = relation_type.replace("'", '').replace('"', '')
    except ValueError:
        raise template.TemplateSyntaxError("'get_relation_type' requires an object, relation_type and a variable name.")
    return RelatedNode(obj, var, relation_type=relation_type)
    

class RelatedNode(template.Node):
    def __init__(self, object, var_name, content_type=None, relation_type=None):
        self.content_type = content_type
        self.relation_type = relation_type
        self.object = template.Variable(object)
        self.var_name = var_name
        
    def render(self, context):
        try:
            the_obj = self.object.resolve(context)
            if self.content_type:
                context[self.var_name] = the_obj.get_related_content_type(self.content_type)
            elif self.relation_type:
                context[self.var_name] = the_obj.get_relation_type(self.relation_type)
            else:
                context[self.var_name] = []
            return ''
        except template.VariableDoesNotExist:
            return ''

class AuthorsByOrderedString(template.Node):
    def __init__(self, authors_related_manager, ordered_string, var_name):
        self.var_name = var_name
        self.ordered_string = template.Variable(ordered_string)
        self.authors_related_manager = template.Variable(authors_related_manager)
        self.var_name = var_name
        
    def render(self, context):
        author_list = []
        link = '<a href="%s">%s %s</a>'
        non_link = '%s %s'
        authors_related_manager = self.authors_related_manager.resolve(context)
        ordered_string = self.ordered_string.resolve(context)
        if ordered_string:
            author_string_list = ordered_string.split(',')
        else:
            author_string_list = []
        ordered_staff_id = []
        for author_string in author_string_list:
            # Because people have spaces in their name, ie middle names and some people decided to put
            # spaces after their name. We are just removing all spaces and querying as case insensitive
            staff_author_qs = authors_related_manager.extra(
                        where=["UPPER(replace(first_name||last_name, ' ',''))=%s"],  
                               params=[author_string.replace(' ', '').upper()])
            if staff_author_qs:
                staff_author = staff_author_qs[0]
                ordered_staff_id.append(staff_author.id)
                
                if hasattr(staff_author, 'get_absolute_url'):
                    text = link % (staff_author.get_absolute_url(), staff_author.first_name, staff_author.last_name)
                else:
                    text = non_link % (staff_author.first_name, staff_author.last_name)

                author_list.append(text)
            else:
                author_list.append(author_string.strip())
                    
        non_ordered_staff_qs = authors_related_manager.exclude(id__in=ordered_staff_id)
        for non_ordered_staff in non_ordered_staff_qs:
            if hasattr(non_ordered_staff, 'get_absolute_url'):
                text = link % (non_ordered_staff.get_absolute_url(), non_ordered_staff.first_name, non_ordered_staff.last_name)
            else:
                text = non_link % ( non_ordered_staff.first_name, non_ordered_staff.last_name)
            author_list.insert(0, text)
        
        if len(author_list) > 1:
            author_string = "%s and %s" % (", ".join(author_list[:-1]), author_list[-1])
        elif len(author_list) == 1:
            author_string = author_list[0]
        else:
            author_string = ''
        
        context[self.var_name] = mark_safe(author_string)
        return ''

@register.tag('display_authors_by_ordered_string')
def do_display_authors_by_ordered_string(parser, token):
    """
    Tag to get a string that contains ordered authors by string and link if applicable
    """
    try:
        tag_name, authors_related_manager, ordered_string,  as_txt, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("'display_authors_by_ordered_string' requires a authors list, string and a variable name.")
    return AuthorsByOrderedString(authors_related_manager, ordered_string, var_name)