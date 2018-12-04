from press.models import PressElement


def test_string_representation():
    attrs = {'some-attr': 'somevalue', 'version': '1.1'}
    attrs_str = 'some-attr="somevalue" version="1.1"'
    content = 'Text and... trailing text!'
    expected = '<sometag %s>%s</sometag>' % (attrs_str, content)
    element = PressElement('sometag', text='Text and', tail=' trailing text!',
                           attrs=attrs)

    assert repr(element) == expected
    assert str(PressElement('tagname')) == '<tagname></tagname>'


def test_tree_behavior():
    pass


def test_iterator_behavior():
    pass


def test_equality_behavior():
    pass


def test_contains_text():
    pass


def test_object_representation():
    # test the `__repr__` method
    pass
