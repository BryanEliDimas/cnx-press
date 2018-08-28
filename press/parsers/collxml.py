#-*- coding: utf-8 -*-

from xml import sax
from collections import namedtuple


def find_differences_in_collections(collection_tree):
    """Returns
    """
    added = []
    removed = []


def create_xml_from_collection_tree(collection_tree):
    from lxml import etree
    root = etree.Element('root')




class NodeBase(object):
    """Represents a collxml element parsed from a Collection xml file.
    It is iterable and it is comparable using `is_equal_to`.
    """
    def __init__(self, name, attrs):
        self.name = name
        self.__children = []
        self.__index = 0
        self.__attrs = attrs


    def __len__(self):
        return len(self.__children)


    def __iter__(self):
        return self


    def __next__(self):
        temp = []

        grandchildren = self.__children[self.__index]
        # loop will run only if there are grandchildren
        for grandchild in grandchildren:
            temp.append(grandchild)
        # so then we return the array
        if len(temp) > 0:
            return temp

        child = self.__children[self.__index]
        grandchildren = [grandchild for grandchild in child]
        if len(grandchildren) > 0:
            return grandchildren


        self.__index += 1
        # otherwise, this will just return the child at calculated index
        return self.__children[self.__index - 1]


    # def next(self): # for backward compatibility with Python 2
    #     return self.__next__()

    def is_equal_to(self, other):
        if not self._same_element_name(other) or not self._same_number_of_children(other):
            return False

        if self._both_have_title(other) and not self._same_title(other):
            return False
        elif self._xor_title(other):
            return False

        for i, node in enumerate(other):
            if not node.is_equal_to(self): # recursion
                return False

        return True


    def _same_number_of_children(self, other):
        return len(self) == len(other)


    def _same_element_name(self, other):
        return self.name == other.name


    def _both_have_title(self, other):
        """True if both nodes are Modules and they have the same title.
        """
        # return hasattr(self, 'title') == hasattr(other, 'title')
        return hasattr(self, 'title') and hasattr(other, 'title')


    def _same_title(self, other):
        return getattr(self, 'title') == getattr(other, 'title')


    def _xor_title(self, other):
        """Returns true if only one of [them] has a title attribute.
        """
        return hasattr(self, 'title') ^ hasattr(other, 'title')


    def insert(self, node):
        self.__children.append(node)
        return self.__children


    # collxml element attributes - maybe a diff class should impl. this
    def element_attributes(self):
        import inspect
        return inspect.getmembers(self, predicate=inspect.ismethod) # array?


    def define_attrs_from_dict(self, attrs):
        """This method defines attributes on instance from a passed-in
        dictionary on instantiation.
        """
        for k, v in self.__attrs:
            setattr(k, v)


"""
SAX parser
"""
class CollectionXmlHandler(sax.ContentHandler):
    """SAX parser for collxml, outputs a tree of objects
    representing the collxml.
    """
    def __init__(self, tree_root):
        self.current_node = tree_root
        # self.current_node.element_attributes()


    def startElementNS(self, name, qname, attrs):
        uri, localname = name
        new_node = self._create_node(localname, self.not_ns_attrs(attrs))
        import pdb; pdb.set_trace()
        self.current_node.insert(new_node)
        self.current_node = new_node


    # def endElementNS(self, name, qname):
    #     uri, localname = name
    #     node = self._create_node(localname)
    #     self.current_node.insert(node)


    def _create_node(self, name, attrs):
        Node = type('Node', (NodeBase,), attrs)
        return Node(name)


    def not_ns_attrs(self, attrs):
        """By default, attrs are namespaced. This func removes namespacing.
        """
        return {nsk[1]: v for nsk, v in dict(attrs).items()}


    # def _create_tuple_node(name, attrs): # experiment
    #     Node = namedtuple(name, string(attrs.keys()))
    #     return Node(string(attrs.values()))



def parse_collxml(input_collxml, tree_root):
    """
    input_collxml should be a filename or a file object
    """
    parser = sax.make_parser()
    parser.setFeature(sax.handler.feature_namespaces, 1)
    parser.setContentHandler(CollectionXmlHandler(tree_root))

    parser.parse(input_collxml)


def test_parser():
    tree_root1 = NodeBase('root')
    tree_root2 = NodeBase('root')

    with open('collection.xml', 'rb') as f:
        parse_collxml(f, tree_root1)

    with open('collection.xml', 'rb') as f:
        parse_collxml(f, tree_root2)


    assert tree_root1.is_equal_to(tree_root2)


test_parser()


# mod1 = Module('title1', '1.0')
# mod2 = Module('title1', '1.0')
# mods = [mod1, mod2]
# subcol1 = [SubCollection(mods)]
# subcol2 = [SubCollection(mods)]
# subcols = [subcol1, subcol2]
# col1 = Collection(subcols)
# col2 = Collection(subcols)
