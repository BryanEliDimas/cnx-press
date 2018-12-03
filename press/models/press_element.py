class PressElement:
    """Represents a collxml element parsed from a Collection XML file.
    It is iterable and it is comparable using `is_equal_to`.
    """
    def __init__(self, tag, attrs=None, text='', tail=''):
        self.tag = tag
        self.text = text
        self.tail = tail
        self.attrs = (attrs and attrs.copy()) or {}
        self.children = []
        self.parent = None

    """Make it hashable so that we can convert the tree to a set and then use
    set operations.
    """
    def __hash__(self):
        return hash((self.tag, self.text, self.tail))

    def __eq__(self, other):
        return hash(self) == hash(other)

    """Represent a tag as it would appear in the source collxml file,
    with the exception that this also includes the trailing text (`tail`)
    prepended with `...` (ellipsis).
    """
    def __repr__(self):
        text = self.text or ''
        tail = self.tail and '...{}'.format(self.tail) or ''
        keyvals = [' %s="%s"' % item for item in self.attrs.items()]
        attr_str = ''.join(keyvals)
        return '<%s%s>%s</%s>' % (self.tag, attr_str, text + tail, self.tag)

    def __str__(self):
        text = self.text or ''
        tail = self.tail and '...{}'.format(self.tail) or ''
        keyvals = [' %s="%s"' % item for item in self.attrs.items()]
        attr_str = ''.join(keyvals)
        return '<%s%s>%s</%s>' % (self.tag, attr_str, text + tail, self.tag)

    """Make its length be the length of its children."""
    def __len__(self):
        return len(self.children)

    """Make it iterable, see also #iter()"""
    def __iter__(self):
        return iter(self.children)

    def iter(self):
        yield self

        for nested in self:
            yield from nested.iter()

    """Make it a tree"""
    def add_child(self, child):
        """Works like append for XML ElementTree-s."""
        child.parent = self
        self.children.append(child)
        # return self

    def getparent(self):
        return self.parent

    def insert_text(self, content):
        content = content.strip()
        if self.text and content:  # if already has text, it's a tail.
            return PressElement(self.tag, attrs=self.attrs, text=self.text,
                                tail=content)
        else:
            return PressElement(self.tag, attrs=self.attrs, text=content)

    def itertext(self):
        tag = self.tag
        if not isinstance(tag, str) and tag is not None:
            return
        if self.text:
            yield self.text
        for e in self:
            for s in e.itertext():
                yield s
            if e.tail:
                yield e.tail

    def complete_title(self):
        text = [t for t in self.itertext()]
        title_as_string = ' '.join(text + [self.tail or '']).strip()
        return title_as_string

    def is_equal_to_tree(self, other):
        """Equality is defined as two collections having the same
        type of tag in the same order and all modules having the same title.
        """
        if self.tag == 'title' and other.tag == 'title':
            """title tags may have nested tags within them,
            so consider the text in those as well for comparison.
            """
            for this, other in zip(self.itertext(), other.itertext()):
                if this != other:
                    return False
                return True
        else:
            # NOTE: Ignores attributes.
            #       Just make sure that it's the same kinda tag.
            return self.tag == other.tag
