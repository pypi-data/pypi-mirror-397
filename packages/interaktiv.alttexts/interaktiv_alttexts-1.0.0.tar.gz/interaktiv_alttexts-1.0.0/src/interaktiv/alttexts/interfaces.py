"""Module where all interfaces, events and exceptions live."""

from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IInteraktivAltTextBrowserLayer(IPloneAppContenttypesLayer, IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""
