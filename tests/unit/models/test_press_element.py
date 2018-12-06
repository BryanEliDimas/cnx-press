from press.models import PressElement


def test_string_representation():
    attrs = {'some-attr': 'somevalue', 'version': '1.1'}
    attrs_str = 'some-attr="somevalue" version="1.1"'
    content = 'Text and... trailing text!'
    expected = '<sometag %s>%s</sometag>' % (attrs_str, content)

    element = PressElement('sometag', text='Text and', tail=' trailing text!',
                           attrs=attrs)
    assert repr(element) == expected

    assert repr(PressElement('tagname')) == '<tagname></tagname>'
    assert str(PressElement('tagname')) == '<tagname></tagname>'
    assert str(PressElement('tagname', text='Yes')) == '<tagname>Yes</tagname>'


def test_tree_behavior():
    t = PressTree()

    dtree = {
        '#collection': [
            {
                '#metadata': [
                    {'#content-id': 'col11405'},
                    {'#title': 'Intro to Computational Engineering'},
                    {'#version': '1.2'},
                ]
            },
            {
                '#content': [
                    {
                        '#module': [
                            {
                                '@document': 'm42303',
                                '@version': 'latest',
                                '@repository': 'http://cnx.org/content',
                                '@version-at-this-collection-version': '1.1'
                            },
                            {
                                '#title': 'Introduction to Quartus.....',
                            }
                        ]
                    },
                    {
                        '#module': [
                            {
                                '@document': 'm42304',
                                '@version': 'latest',
                                '@repository': 'http://cnx.org/content',
                                '@version-at-this-collection-version': '1.3'
                            },
                            {
                                '#title': 'Chapter 1.....',
                            }
                        ]
                    },
                ]
            }
        ]
    }



def test_iterator_behavior():
    pass


def test_equality_behavior():
    pass


def test_contains_text():
    pass


def test_object_representation():
    # test the `__repr__` method
    pass
