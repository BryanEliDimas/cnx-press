from press.models import PressElement, ComparablePressElement as Comparable
from press.parsers import parse_collxml
from press.utils import (
    convert_to_legacy_domain,
    convert_version_to_legacy_version,
    requires_major_version_update,
    diff_collxml,
)


def test_major_version_checker(collxml_templates):
    """No changes in collxml should NOT require a major version update.
    """
    with (collxml_templates / 'original.xml').open('r') as file:
        tree = sametree = parse_collxml(file)
    assert requires_major_version_update(tree, sametree) is False


def test_diffying_collxml_with_additional_modules(collxml_templates):
    """Diffying returns sets of PressElement objects for added & removed.
    """
    with (collxml_templates / 'original.xml').open('r') as doc1, \
         (collxml_templates / 'extra_module.xml').open('r') as doc2:
        tree1 = parse_collxml(doc1)
        tree2 = parse_collxml(doc2)

    diff = diff_collxml(Comparable(tree1), Comparable(tree2))

    added1 = PressElement('title', {})
    added1.text = 'AN ADDITIONAL MODULE'

    # Note: `extra_module.xml` also contains a renamed (title --> TITLE) tag
    added2 = PressElement('TITLE', {})
    added2.text = 'A Student to Student Intro to'
    added2.tail = 'Programming and CCS4'

    # Aforementioned TITLE tag also contains a nested `<code>` tag.
    added3 = PressElement('code', {})
    added3.text = 'IDE'

    removed1 = PressElement('title', {})
    removed1.text = 'A Student to Student Intro to IDE Programming and CCS4'

    expected_removed = set((Comparable(removed1)))
    expected_added = set((Comparable(added1), Comparable(added2),
                          Comparable(added3)))

    assert expected_removed == diff.removed
    assert diff.added == expected_added


def test_a_change_in_title_req_major_change(collxml_templates):
    """A change in a module's title requires a major version update.
    """
    with (collxml_templates / 'original.xml').open('r') as before_doc, \
         (collxml_templates / 'changed_title.xml').open('r') as after_doc:
        tree_before = parse_collxml(before_doc)
        tree_after = parse_collxml(after_doc)

    assert requires_major_version_update(tree_before, tree_after) is True


def test_change_in_the_order_of_mods_req_maj_ver_update(collxml_templates):
    """A change in the order of modules requires a major version update.
    """
    with (collxml_templates / 'original.xml').open('r') as before_doc, \
         (collxml_templates / 'changed_order.xml').open('r') as after_doc:
        tree_before = parse_collxml(before_doc)
        tree_after = parse_collxml(after_doc)

    assert requires_major_version_update(tree_before, tree_after) is True


def test_change_in_title_markup_requires_maj_ver_update(collxml_templates):
    """Text surrounded by markup within titles is considered for equality.
    """
    diff_markup = 'changed_markup_in_title.xml'
    with (collxml_templates / 'markup_in_title.xml').open('r') as before_doc, \
         (collxml_templates / diff_markup).open('r') as after_doc:
        tree_before = parse_collxml(before_doc)
        tree_after = parse_collxml(after_doc)

    assert requires_major_version_update(tree_before, tree_after) is True


def test_module_version():
    version = (4, None)  # Note, modules do not have a minor version
    expected_version = '1.{}'.format(version[0])
    assert convert_version_to_legacy_version(version) == expected_version


def test_collection_version():
    version = (8, 11)
    expected_version = '1.{}'.format(version[0])
    assert convert_version_to_legacy_version(version) == expected_version


class TestConvertToLegacyDomain:

    def test_prod_domain(self):
        domain = 'example.com'
        expected = '.'.join(['legacy', domain])
        assert convert_to_legacy_domain(domain) == expected

    def test_dev_domain(self):
        domain = 'dev.example.com'
        expected = '-'.join(['legacy', domain])
        assert convert_to_legacy_domain(domain) == expected
