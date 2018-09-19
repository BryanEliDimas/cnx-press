class PressElement:
    """Represents a collxml element parsed from a Collection XML file.
    It is iterable and it is comparable using `is_equal_to`.
    """
    def __init__(self, element_name, attrs):
        self.tag = element_name
        self.text = None
        self.tail = None
        self.parent = None
        self.__children = []
        self.attrib = attrs.copy()

    def __repr__(self):
        """Represents a tag as it would appear in the source collxml file,
        with the exception that this also includes the trailing text (`tail`)
        prepended with `...` (elipsis).
        """
        text = self.text or ''
        tail = self.tail and '...{}'.format(self.tail) or ''
        return '<{tag}>{text}{tail}</{tag}>\n'.format(tag=self.tag, text=text,
                                                    tail=tail)

    def __str__(self):
        text = self.text or ''
        tail = self.tail and '...{}'.format(self.tail) or ''
        return '<{tag}>{text}{tail}</{tag}>\n'.format(tag=self.tag, text=text,
                                                    tail=tail)

    def __iter__(self):
        return iter(self.__children)

    def __len__(self):
        return len(self.__children)

    def add_child(self, child):
        """Works like append for XML ElementTree-s.
        """
        if isinstance(child, self.__class__):
            child.parent = self
            self.__children.append(child)
            return self
        else:
            raise TypeError

    def iter(self):
        yield self

        for nested in self:
            yield from nested.iter()

    def getparent(self):
        return self.parent

    def is_equal_to(self, other):
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
            return self.tag == other.tag  # NOTE: ignores attributes

    def insert_text(self, content):
        content = content.strip()
        if self.text and content:  # if already has text, it's a tail.
            self.tail = content
            return
        self.text = content

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

    def _complete_title(self):
        text = [t for t in self.itertext()]
        title_as_string = ' '.join(text + [self.tail or '']).strip()
        return title_as_string


class ComparablePressElement(PressElement):
    """Class for detecting changes in XML documents.
    """
    def __init__(self, elem):
        super().__init__(elem.tag, **elem.attrib)
        self.elem = elem

    def __hash__(self):
        elem = self.elem
        return hash((elem.tag, elem.text, elem.tail))

    def __eq__(self, other):
        elem = self.elem
        return elem.tag == other.tag and elem.text == other.text and \
            elem.tail == other.tail

    def __iter__(self):
        return iter(self.elem)
