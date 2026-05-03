from __future__ import annotations

from dataclasses import dataclass

from presentation_text_export import presentation_to_text, save_presentation_text


@dataclass
class SlideStub:
    number: int
    title: str
    text: list[str]
    subtitle_1: str | None
    subtitle_2: str | None
    subtitle_3: str | None


@dataclass
class PresentationStub:
    theme: str
    slides: list[SlideStub]


def test_presentation_to_text_contains_titles_subtitles_and_bullets():
    data = PresentationStub(
        theme="Test theme",
        slides=[
            SlideStub(
                number=0,
                title="Intro",
                text=["first point", "  second point  ", ""],
                subtitle_1="sub 1",
                subtitle_2=None,
                subtitle_3="sub 3",
            )
        ],
    )

    result = presentation_to_text(data)

    assert "Theme: Test theme" in result
    assert "Slide 1: Intro" in result
    assert "Subtitle 1: sub 1" in result
    assert "Subtitle 3: sub 3" in result
    assert "- first point" in result
    assert "- second point" in result


def test_save_presentation_text_creates_txt_near_presentation(tmp_path):
    data = PresentationStub(
        theme="Theme",
        slides=[
            SlideStub(
                number=0,
                title="Slide",
                text=["text"],
                subtitle_1=None,
                subtitle_2=None,
                subtitle_3=None,
            )
        ],
    )

    presentation_path = tmp_path / "my_presentation.pptx"
    txt_path = save_presentation_text(data, str(presentation_path))

    assert txt_path.endswith(".txt")
    assert (tmp_path / "my_presentation.txt").is_file()
    assert "Theme: Theme" in (tmp_path / "my_presentation.txt").read_text(encoding="utf-8")
