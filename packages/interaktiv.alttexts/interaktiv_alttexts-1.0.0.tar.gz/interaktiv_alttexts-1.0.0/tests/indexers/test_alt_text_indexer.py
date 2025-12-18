from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import plone.api as api


class TestAltTextIndexer:
    def test_index(self, portal):
        # setup
        setRoles(portal, TEST_USER_ID, ["Manager"])

        expected_alt_text = "Test alt text"
        test_image = api.content.create(container=portal, type="Image", id="test_image")
        test_image.alt_text = expected_alt_text

        # do it
        catalog = api.portal.get_tool("portal_catalog")
        results = catalog.unrestrictedSearchResults(UID=test_image.UID())

        # post condition
        assert results[0].alt_text == expected_alt_text
