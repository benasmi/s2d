import json
import uuid
from enum import Enum
import xml.etree.ElementTree as ET

PackagedElementType = {
    "use_case": "uml:UseCase",
    "actor": "uml:Actor",
    "include": "uml:Include",
    "association": "uml:Association"

}


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
    el = ET.Element("uml:Package")
    el.set("xmi:id", uuid.uuid4().hex)
    el.set("xmi:label", package_name)
    el.set("name", package_name)

    return el


def write_xmi(root, filename):
    ET.indent(root, space="\t", level=0)
    xml = ET.tostring(root)

    with open("./data/" + filename + ".xml", "wb") as f:
        f.write(xml)


def create_packaged_el(symbol) -> ET.Element:
    el = ET.Element("packagedElement")
    el.set("xmi:type", PackagedElementType[symbol['type']])
    el.set("xmi:id", symbol['id'])
    if symbol['name']:
        el.set("name", symbol['name'])

    return el


# Read diagram
diagram = json.load(open('./data/diagram.json'))

# Create root element
root_el = create_root_el()
package_el = create_package_el(diagram['name'])
root_el.append(package_el)

# Create packaged elements
packaged_elements = list(map(lambda el: create_packaged_el(el), diagram['elements']))
[root_el.append(el) for el in packaged_elements]

# Write xmi
write_xmi(root_el, diagram['name'])
