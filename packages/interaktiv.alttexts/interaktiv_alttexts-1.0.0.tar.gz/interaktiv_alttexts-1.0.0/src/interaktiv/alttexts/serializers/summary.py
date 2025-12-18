from plone.restapi.interfaces import IJSONSummarySerializerMetadata
from zope.interface import implementer


@implementer(IJSONSummarySerializerMetadata)
class AltTextJSONSummarySerializerMetadata:
    """Additional metadata to be exposed on listings."""

    def default_metadata_fields(self):
        return {"alt_text"}
