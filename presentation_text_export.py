from __future__ import annotations

import os
from typing import Protocol


class SlideLike(Protocol):
    number: int
    title: str
    text: list[str]
    subtitle_1: str | None
    subtitle_2: str | None
    subtitle_3: str | None


class PresentationLike(Protocol):
    theme: str
    slides: list[SlideLike]


def presentation_to_text(data: PresentationLike) -> str:
    lines: list[str] = [f"Theme: {data.theme}", ""]

    for slide in data.slides:
        lines.append(f"Slide {slide.number + 1}: {slide.title}")

        if slide.subtitle_1:
            lines.append(f"Subtitle 1: {slide.subtitle_1}")
        if slide.subtitle_2:
            lines.append(f"Subtitle 2: {slide.subtitle_2}")
        if slide.subtitle_3:
            lines.append(f"Subtitle 3: {slide.subtitle_3}")

        for paragraph in slide.text:
            text = paragraph.strip()
            if text:
                lines.append(f"- {text}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def save_presentation_text(data: PresentationLike, presentation_path: str) -> str:
    txt_path = os.path.splitext(presentation_path)[0] + ".txt"
    presentation_text = presentation_to_text(data)

    with open(txt_path, "w", encoding="utf-8") as txt_file:
        txt_file.write(presentation_text)

    return txt_path
