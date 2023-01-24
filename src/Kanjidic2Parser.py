import pathlib
from dataclasses import dataclass, field
from typing import Dict
from xml.etree.ElementTree import ElementTree


@dataclass
class Kj2Info:
    kanji: str
    grade: int = None
    strokes: int = None
    freq: int = None
    jlpt: int = None
    onyomi: [str] = field(default_factory=lambda: [])
    kunyomi: [str] = field(default_factory=lambda: [])
    nanori: [str] = field(default_factory=lambda: [])
    english: [str] = field(default_factory=lambda: [])


class Kanjidic2Parser:
    def __init__(self, path: pathlib.Path):
        self.path = path
        self.kanji_dict: Dict[str, Kj2Info] = {}

    def parse(self):
        if not self.path.exists():
            raise Exception(f"File '{self.path}' does not exist!")

        self.kanji_dict.clear()
        root = ElementTree().parse(self.path)
        for element in root:
            if element.tag == "character":
                info = Kj2Info(element.find("literal").text)

                grade = element.find("misc/grade")
                if grade is not None:
                    info.grade = int(grade.text)
                strokes = element.find("misc/stroke_count")
                if strokes is not None:
                    info.strokes = int(strokes.text)
                freq = element.find("misc/freq")
                if freq is not None:
                    # print("\tFrequency: " + freq.text + " of 2500 most used in newspapers")
                    info.freq = int(freq.text)
                jlpt = element.find("misc/jlpt")
                if jlpt is not None:
                    info.jlpt = int(jlpt.text)

                rmgroup = element.find("reading_meaning/rmgroup")
                if rmgroup:
                    for rm in rmgroup:
                        if rm.tag == "reading":
                            rtype = rm.attrib.get("r_type")
                            if rtype == "ja_on":
                                info.onyomi.append(rm.text)
                            elif rtype == "ja_kun":
                                info.kunyomi.append(rm.text)
                        elif rm.tag == "meaning":
                            if len(rm.attrib) == 0:
                                info.english.append(rm.text)

                reading_meaning = element.find("reading_meaning")
                if reading_meaning:
                    for rm in reading_meaning:
                        if rm.tag == "nanori":
                            info.nanori.append(rm.text)

                self.kanji_dict[info.kanji] = info