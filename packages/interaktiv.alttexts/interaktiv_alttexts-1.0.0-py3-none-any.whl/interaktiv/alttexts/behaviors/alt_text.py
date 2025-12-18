from interaktiv.alttexts import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import provider


@provider(IFormFieldProvider)
class IAltTextBehavior(model.Schema):
    alt_text = schema.TextLine(
        title=_("alt_text_label", default="Alt text"),
        description=_(
            "alt_text_description",
            default=(
                "An alternative text makes the image accessible for "
                "people using assistive technologies and as fallback for "
                "when the image fails to load. Decorative images should "
                "not have an alternative text."
            ),
        ),
        required=False,
        default="",
    )


class IAltTextMarker(Interface):
    """Marker interface for content that supports alt text."""


@implementer(IAltTextBehavior)
class AltTextAdapter:
    def __init__(self, context):
        self.context = context

    @property
    def alt_text(self):
        return self.context.alt_text

    @alt_text.setter
    def alt_text(self, value):
        self.context.alt_text = value
