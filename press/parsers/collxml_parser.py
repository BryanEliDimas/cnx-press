# XML SAX
# https://docs.python.org/3.7/library/xml.sax.html#module-xml.sax

# __dict__ attribute
#

# XML Schema
# https://github.com/Connexions/cnxml/blob/master/cnxml/xml/collxml/schema/rng/2.0/collxml-defs.rng#L317

# XML template for testing
# https://github.com/Connexions/cnx-press/blob/3759b19ea1d6d2abbd2e1bbf7e44baf8394c9002/tests/_templates/collection.xml

# import xml.etree.ElementTree as ET
# tree = ET.parse('country_data.xml')
# root = tree.getroot()

class Collxml_Parser(object):
  """docstring for Collxml_Parser"""
  def __init__(self, arg):
    self.arg = arg
