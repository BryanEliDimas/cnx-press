#-*- coding: utf-8 -*-

from xml import sax
from collections import namedtuple
import inspect


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
    def __init__(self, name):
        self.name = name
        self.__children = []
        self.__index = 0


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

        # child = self.__children[self.__index]
        # if len(child) > 0:
        #     return temp.extend()


        child = self.__children[self.__index]
        grandchildren = [grandchild for grandchild in child]
        if len(grandchildren) > 0:
            return grandchildren


        self.__index += 1
        # otherwise, this will just return the child at calculated index
        return self.__children[self.__index - 1]


"""
    def __next__(self):
        grandchildren = []

        for node in self.__children:
            if len(node.__children) >= 1: # has a subtree?
                grandchildren.extend(node.__children)

        # if has a subtree?
        node_with_subtree = self.__children[self.__index]
        for subtree in node_with_subtree.__children:
            # iterate through each node of the subtree
            for i, node in enumerate(subtree):
                grandchildren[i].insert(node)
        # else
        for node in self.__children:
            # simply return the node at current index
            return self.__children[self.__index]


    def has_subtree(self):
        for node in self.__children:
            if len(node.__children) > 0:
                return True
            return False


    def __next__(self):
        if self.__index == len(subcollections):
            raise StopIteration

        self.__index += 1
        return self.__children[self.__index - 1]
"""


    # BRYAN - `in` does equality checking though.
    #       consider defining __hash__
    # SO I DON'T THINK THIS WILL WORK.
    # def __contains__(self, node):
    #     if node in self.__children:
    #         return True

    #     for subtree in self.__children:
    #         if node in subtree:
    #             return True

    #     return False


    # def is_root(self):
    #     return len(self.children) == 0 # wrong. this means leaf.


    def is_equal_to(self, other):
        if not _same_element_name(other) or not _same_number_of_children(other):
            return False

        if _both_have_title(other) and not _same_title(other):
            return False
        elif xor_title(other):
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


    def xor_title(self, other):
        """Returns true if only one of [them] has a title attribute.
        """
        return hasattr(self, 'title') ^ hasattr(other, 'title')


    def insert(self, node):
        self.__children.append(node)
        return self.__children


    # collxml element attributes - maybe a diff class should impl. this
    def element_attributes(self):
        return inspect.getmembers(self, predicate=inspect.ismethod) # array?


"""
SAX parser
"""
class CollectionXmlHandler(sax.ContentHandler):
    """SAX parser for collxml, outputs a tree of objects
    representing the collxml.
    """
    def __init__(self):
        self.current_node = []


    def endElementNS(self, (uri, localname), qname):
        node = self._create_node(localname)
        self.current_node.insert(node)

        if localname == 'module':
            pass


    def startElementNS(self, (uris, localname), qname):
        pass


    def _create_node(name, attrs):
        return type(name, (NodeBase,), attrs)


    def _create_tuple_node(name, attrs): # experiment
        Node = namedtuple(name, string(attrs.keys()))
        return Node(string(attrs.values()))



def parse_collxml(input_collxml):
    """
    input_collxml should be a filename or a file object
    """
    parser = sax.make_parser()
    parser.setFeature(sax.handler.feature_namespaces, 0)
    parser.setContentHandler(CollectionXmlHandler())

    parser.parse(input_collxml)


def test_parser():
    pass

mod1 = Module('title1', '1.0')
mod2 = Module('title1', '1.0')
mods = [mod1, mod2]
subcol1 = [SubCollection(mods)]
subcol2 = [SubCollection(mods)]
subcols = [subcol1, subcol2]
col1 = Collection(subcols)
col2 = Collection(subcols)
