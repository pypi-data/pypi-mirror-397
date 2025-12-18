from interaktiv.alttexts import PACKAGE_NAME
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import getUtility

import pytest


class TestSetupUninstall:
    @pytest.fixture(autouse=True)
    def uninstalled(self, installer):
        installer.uninstall_product(PACKAGE_NAME)

    def test_addon_uninstalled(self, installer):
        """Test if interaktiv.alttexts is uninstalled."""
        assert installer.is_product_installed(PACKAGE_NAME) is False

    def test_browserlayer_not_registered(self, browser_layers):
        """Test that IBrowserLayer is not registered."""
        from interaktiv.alttexts.interfaces import IInteraktivAltTextBrowserLayer

        assert IInteraktivAltTextBrowserLayer not in browser_layers

    def test_uninstall_handler(self, portal, installer):
        # setup
        behavior = "interaktiv.alttexts.behavior.alt_text"
        fti = getUtility(IDexterityFTI, name="Image")

        if not installer.is_product_installed(PACKAGE_NAME):
            installer.install_product(PACKAGE_NAME)

        setRoles(portal, TEST_USER_ID, ["Manager"])

        # pre condition
        behaviors = list(fti.behaviors)
        assert behavior in behaviors

        # do it
        installer.uninstall_product(PACKAGE_NAME)

        # post condition
        behaviors = list(fti.behaviors)
        assert behavior not in behaviors
