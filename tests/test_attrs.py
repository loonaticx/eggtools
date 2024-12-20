from eggtools.attributes.EggAlphaAttribute import EggAlpha, EggAlphaAttribute
from eggtools.attributes.EggBackstageAttribute import EggBackstage, EggBackstageAttribute
from eggtools.attributes.EggBillboardAttribute import EggBillboard, EggBillboardAttribute
from eggtools.attributes.EggBinAttribute import EggBin, EggBinAttribute
from eggtools.attributes.EggCollideAttribute import EggCollide, EggCollideAttribute
from eggtools.attributes.EggCollideMaskAttribute import EggCollideMask, EggCollideMaskAttribute
from eggtools.attributes.EggDCSAttribute import EggDCS, EggDCSAttribute
from eggtools.attributes.EggDartAttribute import EggDart, EggDartAttribute
from eggtools.attributes.EggDecalAttribute import EggDecal, EggDecalAttribute
from eggtools.attributes.EggModelAttribute import EggModel, EggModelAttribute
from eggtools.attributes.EggSequenceAttribute import EggSequence, EggSequenceAttribute
from eggtools.attributes.EggTagAttribute import EggTag, EggTagAttribute
from eggtools.attributes.EggExtFileAttribute import EggExtFile, EggExtFileAttribute


def test_egg_attrs():
    """
    Tests instantiation of egg attributes but does not test their application
    """
    for item in ([
        EggAlphaAttribute("Dual"),
        EggBackstageAttribute(),
        EggBillboardAttribute("axis"),
        EggBinAttribute("ground"),
        EggCollideAttribute(csname = 'polygon', flags = [
            name for name in EggCollideAttribute.get_collision_flags().keys()
        ]),
        EggCollideMaskAttribute(value = 'from'),
        EggDCSAttribute("net"),
        EggDartAttribute("structured"),
        EggDecalAttribute(),
        EggExtFileAttribute("dummy.egg"),
        EggExtFileAttribute("tests/test_spot.egg"),
        EggModelAttribute(),
        EggSequenceAttribute(),
        EggTagAttribute("key", "val"),

        # Uncomment to test errors
        # EggDartAttribute("notarealattribute"),
    ]):
        print(item)


if __name__ == "__main__":
    test_egg_attrs()
