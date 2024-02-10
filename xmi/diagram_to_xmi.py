import uuid
import json
from enum import Enum
import xml.etree.ElementTree as ET

PackagedElementType = {
    "use_case": "uml:UseCase",
    "actor": "uml:Actor",
    "include": "uml:Include",
    "association": "uml:Association",
    "extension_point": "uml:ExtensionPoint",
    "extend": "uml:Extend",
    "generalization": "uml:Generalization"
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


def create_packaged_el(symbol) -> ET.Element:
    el = ET.Element("packagedElement")
    el.set("xmi:type", PackagedElementType[symbol['type']])
    el.set("xmi:id", symbol['id'])
    if symbol['name']:
        el.set("name", symbol['name'])

    if 'include' in symbol:
        [el.append(create_include_el(inc)) for inc in symbol['include']]

    if 'extend_from' in symbol:
        extension_point_el = create_extension_point_el(symbol['extend_from'])
        el.append(extension_point_el)

    if 'extend_to' in symbol:
        extend_el = create_extend_el(symbol['extend_to'])
        el.append(extend_el)

    if 'generalization' in symbol:
        [el.append(create_generalization_el(inc)) for inc in symbol['generalization']]

    if 'start' in symbol:
        association_elements = create_association_elements(symbol)
        for assoc_el in association_elements:
            el.append(assoc_el)

    return el


def create_association_elements(symbol):
    assoc_id = symbol['id']

    mem_end_el_1 = ET.Element("memberEnd")
    mem_end_el_1_id = assoc_id + "_member_end_1"
    mem_end_el_1.set("xmi:idref", mem_end_el_1_id)

    mem_end_el_2 = ET.Element("memberEnd")
    mem_end_el_2_id = assoc_id + "_member_end_2"
    mem_end_el_2.set("xmi:idref", mem_end_el_2_id)

    navigable_end_el_1 = ET.Element("navigableOwnedEnd")
    navigable_end_el_1.set("xmi:idref", mem_end_el_1_id)

    navigable_end_el_2 = ET.Element("navigableOwnedEnd")
    navigable_end_el_2.set("xmi:idref", mem_end_el_2_id)

    owned_end_el_1 = ET.Element("ownedEnd")
    owned_end_el_1.set("xmi:type", "uml:Property")
    owned_end_el_1.set("xmi:id", mem_end_el_1_id)
    owned_end_el_1.set("visibility", "private")
    owned_end_el_1.set("type", symbol['start'])
    owned_end_el_1.set("association", assoc_id)

    owned_end_el_2 = ET.Element("ownedEnd")
    owned_end_el_2.set("xmi:type", "uml:Property")
    owned_end_el_2.set("xmi:id", mem_end_el_2_id)
    owned_end_el_2.set("visibility", "private")
    owned_end_el_2.set("type", symbol['end'])
    owned_end_el_2.set("association", assoc_id)

    return [mem_end_el_1, mem_end_el_2, navigable_end_el_1, navigable_end_el_2, owned_end_el_1, owned_end_el_2]


def create_generalization_el(generalization):
    gen_el = ET.Element("generalization")
    gen_el.set("xmi:type", PackagedElementType[generalization['type']])
    gen_el.set("xmi:id", uuid.uuid4().hex)
    gen_el.set("general", generalization['ref'])

    return gen_el


def create_extend_el(extend):
    extend_el = ET.Element("extend")
    extend_el.set("xmi:type", PackagedElementType[extend['type']])
    extend_el.set("xmi:id", extend['extend_id'])
    extend_el.set("visibility", "public")
    extend_el.set("extendedCase", extend['ref'])

    extension_loc_el = ET.Element("extensionLocation")
    extension_loc_el.set("xmi:idref", extend['extension_id'])

    extend_el.append(extension_loc_el)

    return extend_el


def create_extension_point_el(extension_point):
    extension_point_el = ET.Element("extensionPoint")
    extension_point_el.set("xmi:type", PackagedElementType[extension_point['type']])
    extension_point_el.set("xmi:id", extension_point['extension_id'])
    extension_point_el.set("name", extension_point['name'])
    extension_point_el.set("visibility", "public")

    extension_el = ET.Element("extension")
    extension_el.set("xmi:idref", extension_point['extend_id'])

    extension_point_el.append(extension_el)

    return extension_point_el


def create_include_el(include):
    el = ET.Element("include")
    el.set("xmi:type", PackagedElementType[include['type']])
    el.set("xmi:id", uuid.uuid4().hex)
    el.set("visibility", "public")
    el.set("addition", include['ref'])

    return el


def write_xmi(root, filename):
    ET.indent(root, space="\t", level=0)
    xml = ET.tostring(root)

    with open(filename + ".xml", "wb") as f:
        f.write(xml)

    return xml


def convert_to_xmi(diagram):
    # Create root element
    root_el = create_root_el()
    package_el = create_package_el(diagram['name'])
    root_el.append(package_el)

    elements = diagram['elements']

    # Create packaged elements
    packaged_elements = list(map(lambda el: create_packaged_el(el), elements))
    [package_el.append(el) for el in packaged_elements]

    # Write xmi
    return write_xmi(root_el, diagram['name'])


#diagram = json.load(open('./data/diagram.json'))
#convert_to_xmi(diagram)
