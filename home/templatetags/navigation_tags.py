from django import template
from wagtail.core.models import Page
from home.models import FooterLink, FooterImage

register = template.Library()


# Retrieves the top menu items - the immediate children of the parent page
# The has_menu_children method is necessary because the Foundation menu requires
# a dropdown class to be applied to a parent
@register.inclusion_tag('home/top_menu.html', takes_context=True)
def top_menu(context, parent, calling_page=None):
    # Read all pages from DB which are live, has the menue flag and a depth equal to 3,
    # means are all pages below the root/home page
    menuitems = Page.objects.filter(live=True, show_in_menus=True, depth=3)
    if isinstance(parent, Page):
        menuitems = menuitems | parent.get_children().filter(live=True, show_in_menus=True)
    for menuitem in menuitems:
        # We don't directly check if calling_page is None since the template
        # engine can pass an empty string to calling_page
        # if the variable passed as calling_page does not exist.
        menuitem.active = (calling_page.url_path.startswith(menuitem.url_path)
                           if calling_page else False)
    return {
        'calling_page': calling_page,
        'menuitems': menuitems,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


# Footer snippets
@register.inclusion_tag('home/footer.html', takes_context=True)
def footer(context):
    return {
        'footer_links': FooterLink.objects.all(),
        'footer_images': FooterImage.objects.all(),
        'request': context['request'],
    }
