from interaktiv.alttexts.behaviors.alt_text import IAltTextMarker
from plone.indexer import indexer


@indexer(IAltTextMarker)
def alt_text_indexer(obj):
    return getattr(obj, "alt_text", "")
