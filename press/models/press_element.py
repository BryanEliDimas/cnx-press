
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




# class PressTag():
#     """docstring for PressTag"""
#     def __init__(self, name):
#         self.name = name
#         self.attrs = {}

#     def insert_attr(self, attr, val):
#         self.attrs[attr] = val

#     def iter(self):
#         yield self
#         # import pdb; pdb.set_trace()

#         if isinstance(tuple(self)[0], tuple):
#             return

#         for nested in self:
#             yield from nested.iter()



# class PressTree():
#     """bcus trees should behave different than elements"""
#     def __init__(self, dtree):
#         self.root_tag = PressTag('root')
#         self.current_tag = None
#         self.dtree = dtree

#     def from_dict(dtree):
#         res


#     def dict_to_tree(self):
#         import pdb; pdb.set_trace()
#         # dtree must be a dictionary always
#         for items_tuple in self.dtree.items():
#             # the second item in items_tuple could be a list or a dict
#             if isinstance(items_tuple[1], list):
#                 for deep_item in items_tuple[1]:
#                     yield from self.dict_to_tree(items_tuple[1])
#             elif isinstance(items_tuple[1], dict):
#                 yield from self.dict_to_tree(items_tuple[1])
#             elif items_tuple[0].startswith('#'):
#                 if self.current_tag is not None:
#                     new_tag = PressTag(items_tuple[0].strip('#'))
#                     new_tag.parent = self.current_tag
#                     self.current_tag.children.append(new_tag)
#                 else:
#                     self.current_tag = self.root_tag
#                     # self.current_tag.parent = SOMETHING
#             elif items_tuple[0].startswith('@'):
#                 self.current_tag.insert_attr(items_tuple[1].strip('@'))
#             else:
#                 return False
#         return self.root_tag

# tree = PressTree().new_from_dict({'#cool': 'yes'})
# tree = PressTree({'#cool': 'yes'}).dict_to_tree()

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
        # Works like append for XML ElementTree-s
        child.parent = self
        self.children.append(child)

    def insert_text(self, content):
        content = content.strip()
        if self.text and content:  # if already has text, it's a tail.
            return PressElement(self.tag, attrs=self.attrs, text=self.text,
                                tail=content)
        else:
            return PressElement(self.tag, attrs=self.attrs, text=content)

    def itertext(self):
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

    def requires_major_version_update(self, other):
        """Answers the questions:
        - Have any modules been added or removed?
        - Has the order of any of the ~modules~ elements changed?
        - Did the title of any of the modules change?
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
            #       Just make sure that it's the same type of tag.
            return self.tag == other.tag


class PressETree():
    """docstring for PressETree"""
    def __init__(self, root):
        self.current_node = root
        self.next_node = None

    def parse(self, key, val):
        # if val is a string
            # insert text into current node
        # if val is an array
            # handle children # pass-in the children array? and tag name?
        if isinstance(val, str):
            self.current_node.insert_text(val) # handle_characters()
        else: # is a list
            # add a bool flag or insert children into current node
            for item in val:
                import pdb; pdb.set_trace()


        # if key is a tag
            # handle new tag
        # if key is an attribute
            # insert attr to current node
        if key.startswith('#'):  # is a tag
            self.handle_new_tag(key.strip('#'))
        elif key.startswith('@'):  # is an attribute
            self.current_node.attrs[key] = val

    def handle_new_tag(self, tag):
        # create a new PressElement
        # copy over info from current node to the new node
        # set next node
        # replace the current node node's position in its parent's children
        # change the current node to the new one
        new_elem = PressElement(tag)
        new_node.parent = self.current_node
        new_node.children = self.current_node.children

        self.current_node.parent.children.pop()
        self.current_node.parent.children.append(new_node)

        self.current_node = new_node

    def handle_children(self, children):
        # get length of array
            # loop from 0 to array length, keeping track of index
                # for each child,..... call parse?
        for child in children:
            import pdb; pdb.set_trace()
            for key, val in child:
                self.parse(key, val)


def parse_dict_as_press_etree(dtree):
    root_node = PressElement('root')
    press_etree = PressETree(root_node)

    for key, val in dtree.items():
        # import pdb; pdb.set_trace()
        press_etree.parse(key, val)
    return root_node

# tree = PressETree({'#cool': 'yes'}).dict_to_tree()
parse_dict_as_press_etree(dtree)
