import json
import uuid
from enum import Enum
import xml.etree.ElementTree as ET


class SymbolType(Enum):
    use_case = 'use_case'
    actor = 'actor'
    association = 'association'
    association_generalization = 'association_generalization'
    association_include = 'association_include'
    association_exclude = 'association_exclude'


def create_root_el():
    root = ET.Element('xmi:XMI')
    root.set("xmlns:uml", "http://www.omg.org/spec/UML/20110701")
    root.set("xmlns:xmi", "http://www.omg.org/spec/UML/20110701")
    return root


def create_package_el(package_name):
    package_el = ET.Element("uml:Package")
    package_el.set("xmi:id", uuid.uuid4().hex)
    package_el.set("xmi:label", package_name)
    package_el.set("name", package_name)

    return package_el


def write_xmi(root, filename):
    ET.indent(root, space="\t", level=0)
    xml = ET.tostring(root)

    with open("./data/" + filename + ".xml", "wb") as f:
        f.write(xml)


# Read diagram
diagram = json.load(open('./data/diagram.json'))

# Preprocess
root_el = create_root_el()
package_el = create_package_el(diagram['name'])
root_el.append(package_el)

# Write xmi
write_xmi(root_el, diagram['name'])
