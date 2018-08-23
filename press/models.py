from collections import namedtuple


__all__ = ('CollectionMetadata', 'ModuleMetadata',)


CollectionMetadata = namedtuple(
    'CollectionMetadata',
    ('id version created revised title '
     'license_url language print_style '
     'authors maintainers licensors '
     'keywords subjects abstract'),
)

ModuleMetadata = namedtuple(
    'ModuleMetadata',
    ('id version created revised title '
     'license_url language '
     'authors maintainers licensors '
     'keywords subjects abstract'),
)


Resource = namedtuple(
    'Resource',
    ('data filename media_type sha1'),
)


class BaseCxml:
    """
    Base C*XML class
    """
    def __init__(self):
        pass

    def function():
        pass


class Collection:
    """docstring for Collection"""
    def __init__(self, metadata, content, subcollections=[], module=None):
        self.metadata = metadata
        self.content = content
        self.subcollections = subcollections
        self.module = module


    def __eq__(self):
        pass

class SubCollection:
    """docstring for Collection"""
    def __init__(self, title, content):
        self.title = title
        self.content = content


class Module:
    """docstring for Collection"""
    def __init__(self, metadata, title, content):
        self.metadata = metadata
        self.title = title
        self.content = content

