TEXT_FONT: dict[str, dict[str, dict[str, str]]] = {
    "minima": {
        "INITIAL": {
            "TITLE": "Arial Black",
            "TEXT": "Arial"
        },
        "END": {
            "TITLE": "Arial Black",
            "TEXT": "Arial"
        },
        "USUAL": {
            "TITLE": "Arial Black",
            "TEXT": "Arial"
        },
    },
    "2": {
        "INITIAL": {
            "TITLE": "Times New Roman",
            "TEXT": "Times New Roman"
        },
        "END": {
            "TITLE": "Times New Roman",
            "TEXT": "Times New Roman"
        },
        "USUAL": {
            "TITLE": "Times New Roman",
            "TEXT": "Times New Roman"
        },
    },
    "black_study": {
        "INITIAL": {
            "TITLE": "Calibri",
            "TEXT": "Calibri"
        },
        "END": {
            "TITLE": "Calibri",
            "TEXT": "Calibri"
        },
        "USUAL": {
            "TITLE": "Calibri",
            "TEXT": "Calibri"
        },
    },
    "classic": {
        "INITIAL": {
            "TITLE": "Corbel",
            "TEXT": "Corbel"
        },
        "END": {
            "TITLE": "Corbel",
            "TEXT": "Corbel"
        },
        "USUAL": {
            "TITLE": "Corbel",
            "TEXT": "Corbel"
        },
    },
    "kfu": {
        "INITIAL": {
            "TITLE": "PT Sans",
            "TEXT": "PT Sans"
        },
        "END": {
            "TITLE": "PT Sans",
            "TEXT": "PT Sans"
        },
        "USUAL": {
            "TITLE": "PT Sans",
            "TEXT": "PT Sans"
        },
    },
    "style": {
        "INITIAL": {
            "TITLE": "Arial Black",
            "TEXT": "Arial"
        },
        "END": {
            "TITLE": "Arial Black",
            "TEXT": "Arial"
        },
        "USUAL": {
            "TITLE": "Arial Black",
            "TEXT": "Arial"
        },
    }
}

TEXT_FONT_SIZE: dict[str, dict[str, dict[str, int]]] = {
    "minima": {
        "INITIAL": {
            "TITLE": 25,
            "TEXT": 12
        },
        "END": {
            "TITLE": 25,
            "TEXT": 12
        },
        "USUAL": {
            "TITLE": 21,
            "TEXT": 12
        },
    },
    "2": {
        "INITIAL": {
            "TITLE": 58,
            "TEXT": 1
        },
        "END": {
            "TITLE": 58,
            "TEXT": 16
        },
        "USUAL": {
            "TITLE": 42,
            "TEXT": 16
        },
    },
    "black_study": {
        "INITIAL": {
            "TITLE": 52,
            "TEXT": 24
        },
        "END": {
            "TITLE":  52,
            "TEXT": 24
        },
        "USUAL": {
            "TITLE": 42,
            "TEXT": 24
        },
    },
    "classic": {
        "INITIAL": {
            "TITLE": 40,
            "TEXT": 15
        },
        "END": {
            "TITLE": 40,
            "TEXT": 15
        },
        "USUAL": {
            "TITLE": 23,
            "TEXT": 15
        },
    },
    "kfu": {
        "INITIAL": {
            "TITLE": 20,
            "TEXT": 16
        },
        "END": {
            "TITLE": 36,
            "TEXT": 16
        },
        "USUAL": {
            "TITLE": 14,
            "TEXT": 14
        },
    },
    "style": {
        "INITIAL": {
            "TITLE": 33,
            "TEXT": 12
        },
        "END": {
            "TITLE": 34,
            "TEXT": 12
        },
        "USUAL": {
            "TITLE": 24,
            "TEXT": 18
        },
    },
}

MAX_CHARS: dict[str, dict[str, dict[str, dict[str, int]]]] = {
    "minima": {
        "max": {
            "INITIAL": {
                "TITLE": 70
            },
            "END": {
                "TITLE": 25
            },
            "USUAL": {
                "TITLE": 40,
                "TEXT": 900
            },
        },
        "min": {
            "INITIAL": {
                "TITLE": 10
            },
            "END": {
                "TITLE": 10
            },
            "USUAL": {
                "TITLE": 15,
                "TEXT": 300
            },
        }
    },
    "2": {
        "max": {
            "INITIAL": {
                "TITLE": 86
            },
            "END": {
                "TITLE": 86
            },
            "USUAL": {
                "TITLE": 86,
                "TEXT": 915,
            },
        },
        "min": {
            "INITIAL": {
                "TITLE": 70
            },
            "END": {
                "TITLE": 70
            },
            "USUAL": {
                "TITLE": 70,
                "TEXT": 700,
            },
        }
    },
    "black_study": {
        "max": {
            "INITIAL": {
                "TITLE": 86
            },
            "END": {
                "TITLE": 86
            },
            "USUAL": {
                "TITLE": 86,
                "TEXT": 915,
            },
        },
        "min": {
            "INITIAL": {
                "TITLE": 70
            },
            "END": {
                "TITLE": 70
            },
            "USUAL": {
                "TITLE": 70,
                "TEXT": 700,
            },
        }
    },
    "classic": {
        "max": {
            "INITIAL": {
                "TITLE": 50
            },
            "END": {
                "TITLE": 25
            },
            "USUAL": {
                "TITLE": 45,
                "TEXT": 700,
            },
        },
        "min": {
            "INITIAL": {
                "TITLE": 10
            },
            "END": {
                "TITLE": 10
            },
            "USUAL": {
                "TITLE": 15,
                "TEXT": 300,
            },
        }
    },
    "kfu": {
        "max": {
            "INITIAL": {
                "TITLE": 300
            },
            "END": {
                "TITLE": 25
            },
            "USUAL": {
                "TITLE": 210,
                "TEXT": 480,
            },
        },
        "min": {
            "INITIAL": {
                "TITLE": 10
            },
            "END": {
                "TITLE": 10
            },
            "USUAL": {
                "TITLE": 15,
                "TEXT": 200,
            },
        }
    },
    "style":  {
        "max": {
            "INITIAL": {
                "TITLE": 40
            },
            "END": {
                "TITLE": 25
            },
            "USUAL": {
                "TITLE": 40,
                "TEXT": 450
            },
        },
        "min": {
            "INITIAL": {
                "TITLE": 10
            },
            "END": {
                "TITLE": 10
            },
            "USUAL": {
                "TITLE": 15,
                "TEXT": 250
            },
        }
    },
}


TEXT_FONT_SETTINGS: dict[str, dict[str, dict[str, dict[str, bool]]]] = {
    "minima": {
        "INITIAL": {
            "TITLE": {"BOLD": False, "ITALIC": False},
            "TEXT": {"BOLD": False, "ITALIC": False},

        },
        "END": {
            "TITLE": {"BOLD": False, "ITALIC": False},
            "TEXT": {"BOLD": False, "ITALIC": False}
        },
        "USUAL": {
            "TITLE": {"BOLD": False, "ITALIC": False},
            "TEXT": {"BOLD": False, "ITALIC": False},

        },
    },
    "2": {
        "INITIAL": {
            "TITLE": {"BOLD": True, "ITALIC": False},
            "TEXT": {"BOLD": False, "ITALIC": False}
        },
        "END": {
            "TITLE": {"BOLD": True, "ITALIC": False},
            "TEXT": {"BOLD": False, "ITALIC": False}
        },
        "USUAL": {
            "TITLE": {"BOLD": True, "ITALIC": False},
            "TEXT": {"BOLD": False, "ITALIC": False}
        },
    },
    "black_study": {
        "INITIAL": {
            "TITLE": {"BOLD": True, "ITALIC": False},
            "TEXT": {"BOLD": False, "ITALIC": False}
        },
        "END": {
            "TITLE": {"BOLD": True, "ITALIC": False},
            "TEXT": {"BOLD": False, "ITALIC": False}
        },
        "USUAL": {
            "TITLE": {"BOLD": True, "ITALIC": False},
            "TEXT": {"BOLD": False, "ITALIC": False}
        },
    },
    "classic": {
        "INITIAL": {
            "TITLE": {"BOLD": True, "ITALIC": False},
            "TEXT": {"BOLD": False, "ITALIC": False}
        },
        "END": {
            "TITLE": {"BOLD": True, "ITALIC": False},
            "TEXT": {"BOLD": False, "ITALIC": False}
        },
        "USUAL": {
            "TITLE": {"BOLD": True, "ITALIC": False},
            "TEXT": {"BOLD": False, "ITALIC": False}
        },
    },
    "kfu": {
        "INITIAL": {
            "TITLE": {"BOLD": False, "ITALIC": False},
            "TEXT": {"BOLD": False, "ITALIC": False}
        },
        "END": {
            "TITLE": {"BOLD": True, "ITALIC": False},
            "TEXT": {"BOLD": False, "ITALIC": False}
        },
        "USUAL": {
            "TITLE": {"BOLD": True, "ITALIC": False},
            "TEXT": {"BOLD": False, "ITALIC": False}
        },
    },
    "style": {
        "INITIAL": {
            "TITLE": {"BOLD": True, "ITALIC": False},
            "TEXT": {"BOLD": False, "ITALIC": False}
        },
        "END": {
            "TITLE": {"BOLD": True, "ITALIC": False},
            "TEXT": {"BOLD": False, "ITALIC": False}
        },
        "USUAL": {
            "TITLE": {"BOLD": True, "ITALIC": False},
            "TEXT": {"BOLD": False, "ITALIC": False}
        },
    },
}

USUAL_PICTURES: dict[str, list[list[dict[str, str]]]] = {
    "minima": [
        [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "680 561"}],
        [
            {"FIGURE": "ROUNDED RECTANGLE", "SIZE": "550 327"},
            {"FIGURE": "ROUNDED RECTANGLE", "SIZE": "550 327"},
        ],
        [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "748 1080"}],
    ],
    "2": [
        [{"FIGURE": "RECTANGLE", "SIZE": "512 624"}],
        [{"FIGURE": "RECTANGLE", "SIZE": "512 624"}],
        [{"FIGURE": "RECTANGLE", "SIZE": "512 624"}],
        [{"FIGURE": "RECTANGLE", "SIZE": "512 624"}],
    ],
    "black_study": [
        [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "608 512"}],
        [
            {"FIGURE": "ROUNDED RECTANGLE", "SIZE": "512 352"},
            {"FIGURE": "ROUNDED RECTANGLE", "SIZE": "512 352"},
        ],
        [{"FIGURE": "ROUNDED DIAMOND", "SIZE": "512 512"}],
    ],
    "classic": [
        [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "815 1080"}],
        [{"FIGURE": "RECTANGLE", "SIZE": "562 351"}],
        [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "700 700"}],
        [{"FIGURE": "RECTANGLE", "SIZE": "562 351"}],
        [
            {"FIGURE": "ROUNDED RECTANGLE", "SIZE": "780 462"},
            {"FIGURE": "ROUNDED RECTANGLE", "SIZE": "780 462"},
        ],
    ],
    "kfu": [
        [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "700 500"}],
        [],
        [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "700 500"}],
        [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "700 500"}],
        [],
        [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "700 500"}],
        [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "700 500"}],
        [],
        [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "700 500"}],
        []
    ],
    "style": [
        [{"SIZE": "562 351"}],
        [],
        [{"FIGURE": "ROUNDED RECTANGLE", "SIZE": "815 1080"}],
        [
            {"FIGURE": "ROUNDED RECTANGLE", "SIZE": "780 462"},
            {"FIGURE": "ROUNDED RECTANGLE", "SIZE": "780 462"}
        ]
    ],
}

TEXT_COLOR: dict[str, dict[str, dict[str, list[int]]]] = {
    "black_study": {
        "INITIAL": {
            "TITLE": [255, 255, 255],
            "TEXT": [255, 255, 255]
        },
        "END": {
            "TITLE": [255, 255, 255],
            "TEXT": [255, 255, 255]
        },
        "USUAL": {
            "TITLE": [255, 255, 255],
            "TEXT": [255, 255, 255]
        },
    },
    "classic": {
        "INITIAL": {
            "TITLE": [255, 255, 255],
            "TEXT": [255, 255, 255]
        },
        "END": {
            "TITLE": [255, 255, 255],
            "TEXT": [255, 255, 255]
        },
    },
    "kfu": {
        "INITIAL": {
            "TITLE": [255, 255, 255],
            "TEXT": [255, 255, 255]
        },
        "END": {
            "TITLE": [255, 255, 255],
            "TEXT": [255, 255, 255]
        },
    },
    "style": {
        "INITIAL": {
            "TITLE": [255, 255, 255],
            "TEXT": [255, 255, 255]},
        "END": {
            "TITLE": [255, 255, 255],
            "TEXT": [255, 255, 255]
        },
        "USUAL": {
            "TITLE": [255, 255, 255],
            "TEXT": [255, 255, 255]
        },
    },
}

FOREGROUND_IMAGE_SETTINGS: dict[str, list[list[str]]] = {
    "minima": [
        [],
        ["violet_spring.png"],
        [],
    ],
    "black_study": [
        ["yellow_tie.png"],
        [],
        [],
    ],
    "classic": [
        ["blue_square.png"],
        [],
        [],
        [],
        [],
        ["blue_square.png"],
        [],
        [],
        [],
        [],
    ],
}
