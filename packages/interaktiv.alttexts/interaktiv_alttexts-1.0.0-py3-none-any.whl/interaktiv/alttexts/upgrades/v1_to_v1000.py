from Products.CMFPlone.CatalogTool import CatalogTool
from Products.GenericSetup.tool import SetupTool
from Products.ZCatalog.CatalogBrains import AbstractCatalogBrain

import plone.api as api


# noinspection PyUnusedLocal
def upgrade(site_setup: SetupTool | None = None) -> None:
    catalog: CatalogTool = api.portal.get_tool("portal_catalog")

    results: list[AbstractCatalogBrain] = catalog.unrestrictedSearchResults(
        portal_type="Image"
    )

    for brain in results:
        obj = brain.getObject()
        obj.reindexObject()
