import re
from unidecode import unidecode
from xml.etree.ElementTree import ElementTree, Element, SubElement
import sys
from ko2kana import korean2katakana

def process_text(text):
    text = korean2katakana(text)
    return text

xml_file_path = "./voice.xml"
tree = ElementTree()
tree.parse(xml_file_path)

for elem in tree.iter("text"):
    if elem.text is not None:
        elem.text = process_text(elem.text)

processed_xml_file_path = "./voice.xml"
tree.write(processed_xml_file_path, encoding="utf-8")

print(processed_xml_file_path)