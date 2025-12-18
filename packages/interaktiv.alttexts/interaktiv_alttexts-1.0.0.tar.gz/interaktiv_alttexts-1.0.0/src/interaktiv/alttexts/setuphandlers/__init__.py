from plone.base.interfaces import INonInstallable
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import getUtility
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "interaktiv.alttexts:uninstall",
        ]

    def getNonInstallableProducts(self):
        """Hide the upgrades package from site-creation and quickinstaller."""
        return [
            "interaktiv.alttexts.upgrades",
        ]


# noinspection PyUnusedLocal
def uninstall(context):
    # remove behavior
    fti = getUtility(IDexterityFTI, name="Image")
    behavior = "interaktiv.alttexts.behavior.alt_text"

    behaviors = list(fti.behaviors)
    if behavior in behaviors:
        behaviors.remove(behavior)
        fti.behaviors = tuple(behaviors)
