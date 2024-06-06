from typing import TypeAlias, TypeVar

TITLE_TEXT = TypeVar("TITLE_TEXT", dict[str, str], dict[str, bool], dict[str, int])
PICTURE: TypeAlias = list[dict[str, str]]
FOREGROUND: TypeAlias = list[str]

INITIAL_END: TypeAlias = dict[str, TITLE_TEXT]
USUAL: TypeAlias = dict[str, TITLE_TEXT | PICTURE | FOREGROUND]

templates_set: dict[str, dict[str, INITIAL_END | list[USUAL]]] = {
    "1": {
        "INITIAL": {
            "TITLE": {
                "NAME": "Arial Black",
                "SIZE": 46,
                "BOLD": False,
                "ITALIC": False,
            },
            "TEXT": {"NAME": "Arial", "SIZE": 16, "BOLD": False, "ITALIC": False},
        },
        "USUAL": [
            {
                "TITLE": {
                    "NAME": "Arial Black",
                    "SIZE": 30,
                    "BOLD": False,
                    "ITALIC": False,
                },
                "TEXT": {"NAME": "Arial", "SIZE": 16, "BOLD": False, "ITALIC": False},
                "PICTURE": [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "680 561"}],
            },
            {
                "TITLE": {
                    "NAME": "Arial Black",
                    "SIZE": 30,
                    "BOLD": False,
                    "ITALIC": False,
                },
                "TEXT": {"NAME": "Arial", "SIZE": 16, "BOLD": False, "ITALIC": False},
                "PICTURE": [
                    {"FIGURE": "ROUNDED RECTANGLE", "SIZE": "550 327"},
                    {"FIGURE": "ROUNDED RECTANGLE", "SIZE": "550 327"},
                ],
                "FOREGROUND IMAGE": ["violet_spring.png"],
            },
            {
                "TITLE": {
                    "NAME": "Arial Black",
                    "SIZE": 30,
                    "BOLD": False,
                    "ITALIC": False,
                },
                "TEXT": {"NAME": "Arial", "SIZE": 16, "BOLD": False, "ITALIC": False},
                "PICTURE": [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "748 1080"}],
            },
        ],
        "END": {
            "TITLE": {
                "NAME": "Arial Black",
                "SIZE": 46,
                "BOLD": False,
                "ITALIC": False,
            },
            "TEXT": {"NAME": "Arial", "SIZE": 16, "BOLD": False, "ITALIC": False},
        },
    },
    "2": {
        "INITIAL": {
            "TITLE": {
                "NAME": "Times New Roman",
                "SIZE": 58,
                "BOLD": True,
                "ITALIC": False,
            },
            "TEXT": {
                "NAME": "Times New Roman",
                "SIZE": 16,
                "BOLD": False,
                "ITALIC": False,
            },
        },
        "USUAL": [
            {
                "TITLE": {
                    "NAME": "Times New Roman",
                    "SIZE": 42,
                    "BOLD": True,
                    "ITALIC": False,
                },
                "TEXT": {
                    "NAME": "Times New Roman",
                    "SIZE": 16,
                    "BOLD": False,
                    "ITALIC": False,
                },
                "PICTURE": [{"FIGURE": "RECTANGLE", "SIZE": "512 624"}],
            },
            {
                "TITLE": {
                    "NAME": "Times New Roman",
                    "SIZE": 42,
                    "BOLD": True,
                    "ITALIC": False,
                },
                "TEXT": {
                    "NAME": "Times New Roman",
                    "SIZE": 16,
                    "BOLD": False,
                    "ITALIC": False,
                },
                "PICTURE": [{"FIGURE": "RECTANGLE", "SIZE": "512 624"}],
            },
            {
                "TITLE": {
                    "NAME": "Times New Roman",
                    "SIZE": 42,
                    "BOLD": True,
                    "ITALIC": False,
                },
                "TEXT": {
                    "NAME": "Times New Roman",
                    "SIZE": 16,
                    "BOLD": False,
                    "ITALIC": False,
                },
                "PICTURE": [{"FIGURE": "RECTANGLE", "SIZE": "512 624"}],
            },
            {
                "TITLE": {
                    "NAME": "Times New Roman",
                    "SIZE": 42,
                    "BOLD": True,
                    "ITALIC": False,
                },
                "TEXT": {
                    "NAME": "Times New Roman",
                    "SIZE": 16,
                    "BOLD": False,
                    "ITALIC": False,
                },
                "PICTURE": [{"FIGURE": "RECTANGLE", "SIZE": "512 624"}],
            },
        ],
        "END": {
            "TITLE": {
                "NAME": "Times New Roman",
                "SIZE": 58,
                "BOLD": True,
                "ITALIC": False,
            },
            "TEXT": {
                "NAME": "Times New Roman",
                "SIZE": 16,
                "BOLD": False,
                "ITALIC": False,
            },
        },
    },
    "black_study": {
        "INITIAL": {
            "TITLE": {
                "NAME": "Calibri",
                "SIZE": 52,
                "BOLD": True,
                "ITALIC": False,
                "COLOR": [255, 255, 255],
            },
            "TEXT": {
                "NAME": "Calibri",
                "SIZE": 24,
                "BOLD": False,
                "ITALIC": False,
                "COLOR": [255, 255, 255],
            },
        },
        "USUAL": [
            {
                "TITLE": {
                    "NAME": "Calibri",
                    "SIZE": 52,
                    "BOLD": True,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
                "TEXT": {
                    "NAME": "Calibri",
                    "SIZE": 24,
                    "BOLD": False,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
                "PICTURE": [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "608 512"}],
                "FOREGROUND IMAGE": ["yellow_tie.png"],
            },
            {
                "TITLE": {
                    "NAME": "Calibri",
                    "SIZE": 52,
                    "BOLD": True,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
                "TEXT": {
                    "NAME": "Calibri",
                    "SIZE": 24,
                    "BOLD": False,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
                "PICTURE": [
                    {"FIGURE": "ROUNDED RECTANGLE", "SIZE": "512 352"},
                    {"FIGURE": "ROUNDED RECTANGLE", "SIZE": "512 352"},
                ],
            },
            {
                "TITLE": {
                    "NAME": "Calibri",
                    "SIZE": 52,
                    "BOLD": True,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
                "TEXT": {
                    "NAME": "Calibri",
                    "SIZE": 24,
                    "BOLD": False,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
                "PICTURE": [{"FIGURE": "ROUNDED DIAMOND", "SIZE": "512 512"}],
            },
        ],
        "END": {
            "TITLE": {
                "NAME": "Calibri",
                "SIZE": 52,
                "BOLD": True,
                "ITALIC": False,
                "COLOR": [255, 255, 255],
            },
            "TEXT": {
                "NAME": "Calibri",
                "SIZE": 24,
                "BOLD": False,
                "ITALIC": False,
                "COLOR": [255, 255, 255],
            },
        },
    },
    "classic": {
        "INITIAL": {
            "TITLE": {
                "NAME": "Calibri",
                "SIZE": 48,
                "BOLD": True,
                "ITALIC": False,
                "COLOR": [255, 255, 255],
            },
            "TEXT": {
                "NAME": "Calibri",
                "SIZE": 24,
                "BOLD": False,
                "ITALIC": False,
                "COLOR": [255, 255, 255],
            },
        },
        "USUAL": [
            {
                "TITLE": {"NAME": "Corbel", "SIZE": 28, "BOLD": True, "ITALIC": False},
                "TEXT": {"NAME": "Corbel", "SIZE": 18, "BOLD": False, "ITALIC": False},
                "PICTURE": [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "1000 512"}],
                "FOREGROUND IMAGE": ["blue_square.png"],
            },
            {
                "TITLE": {"NAME": "Corbel", "SIZE": 28, "BOLD": True, "ITALIC": False},
                "TEXT": {"NAME": "Corbel", "SIZE": 18, "BOLD": False, "ITALIC": False},
                "PICTURE": [{"FIGURE": "RECTANGLE", "SIZE": "512 680"}],
            },
            {
                "TITLE": {"NAME": "Corbel", "SIZE": 28, "BOLD": True, "ITALIC": False},
                "TEXT": {"NAME": "Corbel", "SIZE": 18, "BOLD": False, "ITALIC": False},
                "PICTURE": [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "512 512"}],
            },
            {
                "TITLE": {"NAME": "Corbel", "SIZE": 28, "BOLD": True, "ITALIC": False},
                "TEXT": {"NAME": "Corbel", "SIZE": 18, "BOLD": False, "ITALIC": False},
                "PICTURE": [{"FIGURE": "RECTANGLE", "SIZE": "640 512"}],
            },
            {
                "TITLE": {"NAME": "Corbel", "SIZE": 28, "BOLD": True, "ITALIC": False},
                "TEXT": {"NAME": "Corbel", "SIZE": 18, "BOLD": False, "ITALIC": False},
                "PICTURE": [
                    {"FIGURE": "ROUNDED RECTANGLE", "SIZE": "512 680"},
                    {"FIGURE": "ROUNDED RECTANGLE", "SIZE": "512 680"},
                ],
            },
            {
                "TITLE": {"NAME": "Corbel", "SIZE": 28, "BOLD": True, "ITALIC": False},
                "TEXT": {"NAME": "Corbel", "SIZE": 18, "BOLD": False, "ITALIC": False},
                "PICTURE": [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "1000 512"}],
                "FOREGROUND IMAGE": ["blue_square.png"],
            },
            {
                "TITLE": {
                    "NAME": "Corbel",
                    "SIZE": 28,
                    "BOLD": True,
                    "ITALIC": False,
                },
                "TEXT": {"NAME": "Corbel", "SIZE": 18, "BOLD": False, "ITALIC": False},
                "PICTURE": [{"FIGURE": "RECTANGLE", "SIZE": "512 680"}],
            },
            {
                "TITLE": {"NAME": "Corbel", "SIZE": 28, "BOLD": True, "ITALIC": False},
                "TEXT": {"NAME": "Corbel", "SIZE": 18, "BOLD": False, "ITALIC": False},
                "PICTURE": [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "512 512"}],
            },
            {
                "TITLE": {"NAME": "Corbel", "SIZE": 28, "BOLD": True, "ITALIC": False},
                "TEXT": {"NAME": "Corbel", "SIZE": 18, "BOLD": False, "ITALIC": False},
                "PICTURE": [{"FIGURE": "RECTANGLE", "SIZE": "640 512"}],
            },
            {
                "TITLE": {"NAME": "Corbel", "SIZE": 28, "BOLD": True, "ITALIC": False},
                "TEXT": {"NAME": "Corbel", "SIZE": 18, "BOLD": False, "ITALIC": False},
                "PICTURE": [
                    {"FIGURE": "ROUNDED RECTANGLE", "SIZE": "512 680"},
                    {"FIGURE": "ROUNDED RECTANGLE", "SIZE": "512 680"},
                ],
            },
        ],
        "END": {
            "TITLE": {
                "NAME": "Calibri",
                "SIZE": 52,
                "BOLD": True,
                "ITALIC": False,
                "COLOR": [255, 255, 255],
            },
            "TEXT": {
                "NAME": "Calibri",
                "SIZE": 24,
                "BOLD": False,
                "ITALIC": False,
                "COLOR": [255, 255, 255],
            },
        },
    },
    "kfu": {
        "INITIAL": {
            "TITLE": {
                "NAME": "Arial",
                "SIZE": 48,
                "BOLD": True,
                "ITALIC": False,
                "COLOR": [255, 255, 255],
            },
            "TEXT": {
                "NAME": "Arial",
                "SIZE": 16,
                "BOLD": False,
                "ITALIC": False,
                "COLOR": [255, 255, 255],
            },
        },
        "USUAL": [
            {
                "TITLE": {"NAME": "Arial", "SIZE": 32, "BOLD": True, "ITALIC": False},
                "TEXT": {"NAME": "Arial", "SIZE": 16, "BOLD": False, "ITALIC": False},
                "PICTURE": [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "512 680"}],
            },
            {
                "TITLE": {"NAME": "Arial", "SIZE": 32, "BOLD": True, "ITALIC": False},
                "TEXT": {"NAME": "Arial", "SIZE": 16, "BOLD": False, "ITALIC": False},
            },
            {
                "TITLE": {"NAME": "Arial", "SIZE": 32, "BOLD": True, "ITALIC": False},
                "TEXT": {"NAME": "Arial", "SIZE": 16, "BOLD": False, "ITALIC": False},
                "PICTURE": [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "512 680"}],
            },
            {
                "TITLE": {"NAME": "Arial", "SIZE": 32, "BOLD": True, "ITALIC": False},
                "TEXT": {"NAME": "Arial", "SIZE": 16, "BOLD": False, "ITALIC": False},
                "PICTURE": [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "512 680"}],
            },
            {
                "TITLE": {"NAME": "Arial", "SIZE": 32, "BOLD": True, "ITALIC": False},
                "TEXT": {"NAME": "Arial", "SIZE": 16, "BOLD": False, "ITALIC": False},
            },
            {
                "TITLE": {"NAME": "Arial", "SIZE": 32, "BOLD": True, "ITALIC": False},
                "TEXT": {"NAME": "Arial", "SIZE": 16, "BOLD": False, "ITALIC": False},
                "PICTURE": [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "512 680"}],
            },
            {
                "TITLE": {
                    "NAME": "Arial",
                    "SIZE": 32,
                    "BOLD": True,
                    "ITALIC": False,
                },
                "TEXT": {"NAME": "Arial", "SIZE": 16, "BOLD": False, "ITALIC": False},
                "PICTURE": [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "512 680"}],
            },
            {
                "TITLE": {"NAME": "Arial", "SIZE": 32, "BOLD": True, "ITALIC": False},
                "TEXT": {"NAME": "Arial", "SIZE": 16, "BOLD": False, "ITALIC": False},
            },
            {
                "TITLE": {"NAME": "Arial", "SIZE": 32, "BOLD": True, "ITALIC": False},
                "TEXT": {"NAME": "Arial", "SIZE": 16, "BOLD": False, "ITALIC": False},
                "PICTURE": [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "512 680"}],
            },
            {
                "TITLE": {"NAME": "Arial", "SIZE": 32, "BOLD": True, "ITALIC": False},
                "TEXT": {"NAME": "Arial", "SIZE": 16, "BOLD": False, "ITALIC": False},
            },
        ],
        "END": {
            "TITLE": {
                "NAME": "Arial",
                "SIZE": 52,
                "BOLD": True,
                "ITALIC": False,
                "COLOR": [255, 255, 255],
            },
            "TEXT": {
                "NAME": "Arial",
                "SIZE": 16,
                "BOLD": False,
                "ITALIC": False,
                "COLOR": [255, 255, 255],
            },
        },
    },
    "techno": {
        "INITIAL": {
            "TITLE": {
                "NAME": "Arial",
                "SIZE": 48,
                "BOLD": True,
                "ITALIC": False,
                "COLOR": [255, 255, 255],
            },
            "TEXT": {
                "NAME": "Arial",
                "SIZE": 16,
                "BOLD": False,
                "ITALIC": False,
                "COLOR": [255, 255, 255],
            },
        },
        "USUAL": [
            {
                "TITLE": {
                    "NAME": "Arial",
                    "SIZE": 32,
                    "BOLD": True,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
                "TEXT": {
                    "NAME": "Arial",
                    "SIZE": 16,
                    "BOLD": False,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
                "PICTURE": [{"SIZE": "512 680"}],
            },
            {
                "TITLE": {
                    "NAME": "Arial",
                    "SIZE": 32,
                    "BOLD": True,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
                "TEXT": {
                    "NAME": "Arial",
                    "SIZE": 16,
                    "BOLD": False,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
            },
            {
                "TITLE": {
                    "NAME": "Arial",
                    "SIZE": 32,
                    "BOLD": True,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
                "TEXT": {
                    "NAME": "Arial",
                    "SIZE": 16,
                    "BOLD": False,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
                "PICTURE": [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "1016 512"}],
            },
            {
                "TITLE": {
                    "NAME": "Arial",
                    "SIZE": 32,
                    "BOLD": True,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
                "TEXT": {
                    "NAME": "Arial",
                    "SIZE": 16,
                    "BOLD": False,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
            },
            {
                "TITLE": {
                    "NAME": "Arial",
                    "SIZE": 32,
                    "BOLD": True,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
                "TEXT": {
                    "NAME": "Arial",
                    "SIZE": 16,
                    "BOLD": False,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
                "PICTURE": [{"SIZE": "512 680"}],
            },
            {
                "TITLE": {
                    "NAME": "Arial",
                    "SIZE": 32,
                    "BOLD": True,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
                "TEXT": {
                    "NAME": "Arial",
                    "SIZE": 16,
                    "BOLD": False,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
            },
            {
                "TITLE": {
                    "NAME": "Arial",
                    "SIZE": 32,
                    "BOLD": True,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
                "TEXT": {
                    "NAME": "Arial",
                    "SIZE": 16,
                    "BOLD": False,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
                "PICTURE": [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "1016 512"}],
            },
            {
                "TITLE": {
                    "NAME": "Arial",
                    "SIZE": 32,
                    "BOLD": True,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
                "TEXT": {
                    "NAME": "Arial",
                    "SIZE": 16,
                    "BOLD": False,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
            },
            {
                "TITLE": {
                    "NAME": "Arial",
                    "SIZE": 32,
                    "BOLD": True,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
                "TEXT": {
                    "NAME": "Arial",
                    "SIZE": 16,
                    "BOLD": False,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
                "PICTURE": [{"SIZE": "512 680"}],
            },
            {
                "TITLE": {
                    "NAME": "Arial",
                    "SIZE": 32,
                    "BOLD": True,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
                "TEXT": {
                    "NAME": "Arial",
                    "SIZE": 16,
                    "BOLD": False,
                    "ITALIC": False,
                    "COLOR": [255, 255, 255],
                },
            },
        ],
        "END": {
            "TITLE": {
                "NAME": "Arial",
                "SIZE": 52,
                "BOLD": True,
                "ITALIC": False,
                "COLOR": [255, 255, 255],
            },
            "TEXT": {
                "NAME": "Arial",
                "SIZE": 16,
                "BOLD": False,
                "ITALIC": False,
                "COLOR": [255, 255, 255],
            },
        },
    },
}
