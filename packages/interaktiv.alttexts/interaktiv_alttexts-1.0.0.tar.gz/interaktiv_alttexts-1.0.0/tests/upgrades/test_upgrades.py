from interaktiv.alttexts.upgrades import v1_to_v1000
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.ZCatalog.CatalogBrains import AbstractCatalogBrain

import plone.api as api


class TestUpgrades:
    def test_upgrade_v1_to_v1000(self, portal):
        # setup
        catalog = api.portal.get_tool("portal_catalog")

        setRoles(portal, TEST_USER_ID, ["Manager"])
        test_image = api.content.create(container=portal, type="Image", id="test_image")

        # pre condition - satisfy the type checker warning
        # "Local variable 'catalog' might be referenced before assignment"
        assert catalog is not None

        # do it
        v1_to_v1000.upgrade()

        # post condition
        results: list[AbstractCatalogBrain] = catalog.unrestrictedSearchResults(
            UID=test_image.UID()
        )

        # this shouldn't raise an AttributeError
        _ = results[0].alt_text
