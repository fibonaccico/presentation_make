from dataclasses import dataclass


@dataclass
class TextDTO:
    titles: list[str]
    slides_text_list: list[str]
    picture_discription_list: list[str]
    fulltext: str
