from dataclasses import dataclass


@dataclass
class TextDTO:
    titles: list[str]
    slides_text_list: list[list[str]]
    picture_discription_list: list[str]
    fulltext: str
    theme: str
    subtitles_1: list[str] | None = None
    subtitles_2: list[str] | None = None
    subtitles_3: list[str] | None = None
