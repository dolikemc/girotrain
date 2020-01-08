from django.db import models
from modelcluster.models import ClusterableModel, ParentalKey
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, RichTextField, FieldRowPanel
from wagtail.core.models import Page, Orderable
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.models import register_snippet

from girotrain.utilities import TranslatedField


class HomePage(Page):
    # title is used for title in German
    title_it = models.CharField(max_length=256, blank=True)
    # 1st body bilingual
    body_top_de = RichTextField(blank=True, default="",
                                features=['h2', 'h3', 'bold', 'italic', 'ol', 'ul', 'hr', 'link'])
    body_top_it = RichTextField(blank=True, default="",
                                features=['h2', 'h3', 'bold', 'italic', 'ol', 'ul', 'hr', 'link'])
    # optional link after the 1st body
    link_top = models.URLField(blank=True)
    link_text_top = models.CharField(max_length=256, blank=True)
    # 2nd body bilingual
    body_bottom_de = RichTextField(blank=True, default="",
                                   features=['h2', 'h3', 'bold', 'italic', 'ol', 'ul', 'hr', 'link'])
    body_bottom_it = RichTextField(blank=True, default="",
                                   features=['h2', 'h3', 'bold', 'italic', 'ol', 'ul', 'hr', 'link'])
    # optional link after the 2nd body
    link_bottom = models.URLField(blank=True)
    link_text_bottom = models.CharField(max_length=256, blank=True)
    content_panels = [
        FieldRowPanel(
            [
                FieldPanel('title'),
                FieldPanel('title_it'),
            ]
        ),
        FieldRowPanel(
            [
                FieldPanel('body_top_de'),
                FieldPanel('body_top_it'),
            ]
        ),
        FieldRowPanel([
            FieldPanel('link_top'), FieldPanel('link_text_top')
        ]),
        InlinePanel('home_page_images', label="Images"),
        FieldRowPanel(
            [
                FieldPanel('body_bottom_de'),
                FieldPanel('body_bottom_it'),
            ]
        ),

        FieldRowPanel([
            FieldPanel('link_bottom'), FieldPanel('link_text_bottom')
        ]),

    ]
    translated_title = TranslatedField(
        'title',
        'title_it',
    )
    body_top = TranslatedField(
        'body_top_de',
        'body_top_it',
    )
    body_bottom = TranslatedField(
        'body_bottom_de',
        'body_bottom_it',
    )
    show_in_menus_default = True


class HomePageImage(Orderable):
    page = ParentalKey(HomePage, on_delete=models.CASCADE, related_name='home_page_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.SET_NULL, related_name='+', null=True, blank=True,
    )
    panels = [
        ImageChooserPanel('image')
    ]


@register_snippet
class Footer(ClusterableModel):
    name = models.CharField(max_length=64, default='Footer')
    panels = [
        FieldPanel('name'),
        InlinePanel('footer_link', label='Links'),
        InlinePanel('footer_image', label='Logos'),
    ]

    def __str__(self) -> str:
        return self.name


class FooterLink(Orderable):
    footer = ParentalKey(to=Footer, on_delete=models.CASCADE, related_name='footer_link')
    url = models.URLField(max_length=255)
    text = models.CharField(max_length=255)

    panels = [
        FieldPanel('url'),
        FieldPanel('text'),
    ]

    def __str__(self) -> str:
        return self.text


class FooterImage(Orderable):
    footer = ParentalKey(to=Footer, on_delete=models.CASCADE, related_name='footer_image')
    url = models.URLField(max_length=255)
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.SET_NULL, related_name='+', null=True, blank=True,
    )

    panels = [
        FieldPanel('url'),
        ImageChooserPanel('image'),
    ]

    def __str__(self) -> str:
        return str(self.url)


class AccordionPage(Page):
    # title is used for title in German
    title_it = models.CharField(max_length=256, blank=True)
    # 1st body bilingual
    body_top_de = RichTextField(blank=True, default="",
                                features=['h2', 'h3', 'bold', 'italic', 'ol', 'ul', 'hr', 'link'])
    body_top_it = RichTextField(blank=True, default="",
                                features=['h2', 'h3', 'bold', 'italic', 'ol', 'ul', 'hr', 'link'])

    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.SET_NULL, related_name='+', null=True, blank=True,
    )
    content_panels = [
        FieldRowPanel(
            [
                FieldPanel('title'),
                FieldPanel('title_it'),
            ]
        ),
        FieldRowPanel(
            [
                FieldPanel('body_top_de'),
                FieldPanel('body_top_it'),
            ]
        ),
        ImageChooserPanel('image'),
        InlinePanel('entry', label='accordion entry'),
    ]
    translated_title = TranslatedField(
        'title',
        'title_it',
    )
    body_top = TranslatedField(
        'body_top_de',
        'body_top_it',
    )


class AccordionEntry(Orderable):
    accordion_page = ParentalKey(to=AccordionPage, on_delete=models.CASCADE, related_name='entry')

    header_de = models.CharField(max_length=128)
    header_it = models.CharField(max_length=128)
    body_de = RichTextField(blank=True, default="",
                            features=['h2', 'h3', 'bold', 'italic', 'ol', 'ul', 'hr', 'link'])
    body_it = RichTextField(blank=True, default="",
                            features=['h2', 'h3', 'bold', 'italic', 'ol', 'ul', 'hr', 'link'])
    header = TranslatedField(
        'header_de',
        'header_it',
    )
    body = TranslatedField(
        'body_de',
        'body_it',
    )
    show_in_menus_default = True

    def __str__(self) -> str:
        return self.body_de
