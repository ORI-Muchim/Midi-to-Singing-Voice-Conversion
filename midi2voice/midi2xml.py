# -*- coding: utf-8 -*-

from sys import platform
import re
import os
import sys
from unidecode import unidecode
from xml.etree.ElementTree import ElementTree, Element, SubElement
from ko2kana import korean2katakana
from .lyrics_tokenizer import tokenize

def process_text(text):
    text = korean2katakana(text) # or replace it with the appropriate function
    return text

def midi2xml(lyrics, midi_path, xml_path, tempo=80, lang="english"):
    temp_xml = "temp.xml"
    create_music_xml(midi_path, temp_xml)
    if lang in ["mandarin", "japanese", "korean"]:
        lyrics = ''.join(lyrics).encode('utf-8').decode('utf-8').replace(' ', '')  # convert list of strings to a single string
        lyrics = list(lyrics)
    else:
        lyrics = tokenize(lyrics, midi_path)
    generate_voice_specification(lyrics, tempo, temp_xml, xml_path, lang)
    os.remove(temp_xml)

def create_music_xml(midi_path, new_musicxml_path):
    if platform in ["win32", "cygwin"]:
        os.system("MuseScore3.exe " + midi_path + " -o " + new_musicxml_path)
    elif platform == "darwin":
        os.system("export QT_QPA_PLATFORM=offscreen && mscore " + midi_path + " -o " + new_musicxml_path)
    else:
        os.system("export QT_QPA_PLATFORM=offscreen && musescore " + midi_path + " -o " + new_musicxml_path)

def generate_voice_specification(lyrics, tempo, input_music_xml_path, output_music_xml_path, lang):
    with open(input_music_xml_path, 'r', encoding='utf-8') as c:
        content = [x.strip() for x in c.readlines()]
        with open(output_music_xml_path, 'w', encoding='utf-8') as f:
            f.write(add_voice_tags(tempo, lyrics, content, lang))

def add_voice_tags(tempo, text, content, lang):
    output = ""
    lyrics_xml = '<voice>1</voice>\n<lyric>\n<syllabic>{}</syllabic>\n<text>{}</text>\n</lyric>\n'

    i = 0
    ignore_this_note = False
    prev_beginning = False
    for line in content:
        if "<rest/>" in line or '<tie type="stop"/>' in line:
            ignore_this_note = True
        if "</note" in line:
            if not ignore_this_note:
                next_part = text[i % len(text)]
                if lang == "korean":
                    next_part = process_text(next_part)
                if next_part.endswith("-"):
                    next_part = next_part[:-1]
                    if prev_beginning:
                        syllabic = "middle"
                    else:
                        syllabic = "begin"
                        prev_beginning = True
                else:
                    if prev_beginning:
                        syllabic = "end"
                    else:
                        syllabic = "single"
                    prev_beginning = False
                output += lyrics_xml.format(syllabic, next_part)
                i += 1
            else:
                ignore_this_note = False

        output += line

    output = re.sub(r"<per-minute>\d+</per-minute>", f"<per-minute>{tempo}</per-minute>", output)
    output = re.sub(r'<sound tempo="\d+"/>', f'<sound tempo="{tempo}"/>', output)

    return output
