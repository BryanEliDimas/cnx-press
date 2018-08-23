#-*- coding: utf-8 -*-

from xml import sax
from collections import namedtuple


class BaseCollection:
    def __init__(self, subcollections=[]):
        self.subcollections = subcollections
        self.index = 0
        self.content = content


    def __iter__(self):
        return self


    def __next__(self):
        if self.index == len(subcollections):
            raise StopIteration

        self.index += 1
        return self.subcollections[self.index]


    def __eq__(self, other):
        if self.index == 0:
            if len(self.subcollections) == 0 and len(self.modules) == 0:
                return True # TODO: check that my logic is fine here

        if len(self.subcollections) != len(other.subcollections) or
           len(self.modules) != len(other.modules):
            return False

        for subcoll in self.subcollections:
            if subcoll not in other.subcollections:
                return False
            return True # hm...

        for mod in self.modules:
            if mod not in other.modules:
                return False
            return True # hm...

        return True # or should I just leave this line in place for the two other return-s?


    def __sub__(self, other):
        if len(self.subcollections) == 0 and len(self.modules) == 0:
            return []

        if len(self.subcollections) > 0:
            subcols = self.subcollections
            return [subcol for subcol in subcols if subcol not in other.subcollections]

        if len(self.modules) > 0:
            mods = self.modules
            return [module for module in modules if module not in other.modules]


    def insert(self, obj):
        # if not isinstance(sub_collection, (SubCollection, CollContent, Module,)): # hm...
        #     raise Exception # TypeMismatch or something
        if isinstance(obj, SubCollection):
            self.subcollections.append(obj)
        elif isinstance(self, SubCollection) and isinstance(obj, SubCollection):
            self.insert(obj)
        elif isinstance(obj, Module)
            self.modules.append(obj)
        else:
            raise Exception

        return self # OR return True OR return obj



class Collection:
    def __init__(self, content=None):
        self.content = content



class CollContent(BaseCollection):
    pass



class SubCollection(BaseCollection):
    """Collection type, nested within another Collection,
    which contains Module-s instead of SubCollection-s.
    """
    def __init__(self, subcollections=[], modules=[], title=None):
        super().__init__(subcollections, modules)
        self.title = title


    def __iter__(self):
        return self


    def __next__(self):
        if self.index == len(modules):
            raise StopIteration

        self.index += 1
        return self.modules[self.index]


    def __eq__(self, other):
        if len(self.modules) != len(other.modules):
            return False

        for mod in self.modules:
            if mod not in other.modules:
                return False
        return True


class Module:
    def __init__(self, title, version):
        self.title = title
        self.version = version


    def __eq__(self, other):
        return self.title == other.title


"""
SAX parser
"""
class CollectionXmlHandler(sax.ContentHandler):
    """SAX parser for collxml, outputs a tree of objects
    representing the collxml.
    """
    def __init__(self):
        self.collection = None
        self.subcollection = None


    def startElementNS(self, (uri, localname), qname, attrs):
        if localname == 'collection':
            self.collection = Collection()
        elif localname == 'content':
            self.collection.content = attr([])


    def endElementNS(self, (uris, localname), qname):
        # if localname ==

def parse_collxml(input_collxml):
    """
    input_collxml should be a filename or a file object
    """
    parser = sax.make_parser()
    parser.setFeature(sax.handler.feature_namespaces, 1)
    parser.setContentHandler(CollectionXmlHandler())

    parser.parse(input_collxml)


mod1 = Module('title1', '1.0')
mod2 = Module('title1', '1.0')
mods = [mod1, mod2]
subcol1 = [SubCollection(mods)]
subcol2 = [SubCollection(mods)]
subcols = [subcol1, subcol2]
col1 = Collection(subcols)
col2 = Collection(subcols)


assert col1 == col2
assert subcol1 == subcol2
assert mod1 == mod2

print col1 == col2
print subcol1 == subcol2
print mod1 == mod2
