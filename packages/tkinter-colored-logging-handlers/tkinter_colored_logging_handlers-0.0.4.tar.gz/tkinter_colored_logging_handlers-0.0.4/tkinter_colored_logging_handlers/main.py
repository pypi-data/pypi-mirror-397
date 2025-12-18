from logging import Handler, LogRecord


class StyleSchemeBase:
    @staticmethod
    def check():
        for i in range(1, 150):
            print(f"\033[{i}m[{i}]\033[0m", end="")

    @classmethod
    def to_dict(cls):
        return {
            k: v
            for k in dir(cls)
            if not k.startswith("_") and isinstance(v := getattr(cls, k), tuple)
        }


class FontScheme:
    BOLD = ("BOLD", "1", {"font": ("", 12, "bold")})
    ITALIC = ("ITALIC", "3", {"font": ("", 12, "italic")})
    UNDERLINE = ("UNDERLINE", "4", {"underline": True})
    BLINK = ("BLINK", "5", {"overstrike": True})
    REVERSE = ("REVERSE", "7", {"overstrike": True})
    STRIKE = ("STRIKE", "9", {"overstrike": True})


class ColorScheme:
    BLACK = ("BLACK", "30", {"foreground": "#000000"})
    RED = ("RED", "31", {"foreground": "#FF0000"})
    GREEN = ("GREEN", "32", {"foreground": "#00FF00"})
    YELLOW = ("YELLOW", "33", {"foreground": "#FFFF00"})
    BLUE = ("BLUE", "34", {"foreground": "#0000FF"})
    PURPLE = ("PURPLE", "35", {"foreground": "#FF00FF"})
    SKYBLUE = ("SKYBLUE", "36", {"foreground": "#00FFFF"})
    WHITE = ("WHITE", "37", {"foreground": "#FFFFFF"})

    BG_BLACK = ("BG_BLACK", "40", {"background": "#000000"})
    BG_RED = ("BG_RED", "41", {"background": "#FF0000"})
    BG_GREEN = ("BG_GREEN", "42", {"background": "#00FF00"})
    BG_YELLOW = ("BG_YELLOW", "43", {"background": "#FFFF00"})
    BG_BLUE = ("BG_BLUE", "44", {"background": "#0000FF"})
    BG_PURPLE = ("BG_PURPLE", "45", {"background": "#FF00FF"})
    BG_SKYBLUE = ("BG_SKYBLUE", "46", {"background": "#00FFFF"})
    BG_WHITE = ("BG_WHITE", "47", {"background": "#FFFFFF"})

    BG_BLACK_BRIGHT = ("BG_BLACK_BRIGHT", "100", {"background": "#000000"})
    BG_RED_BRIGHT = ("BG_RED_BRIGHT", "101", {"background": "#FF0000"})
    BG_GREEN_BRIGHT = ("BG_GREEN_BRIGHT", "102", {"background": "#00FF00"})
    BG_YELLOW_BRIGHT = ("BG_YELLOW_BRIGHT", "103", {"background": "#FFFF00"})
    BG_BLUE_BRIGHT = ("BG_BLUE_BRIGHT", "104", {"background": "#0000FF"})
    BG_PURPLE_BRIGHT = ("BG_PURPLE_BRIGHT", "105", {"background": "#FF00FF"})
    BG_SKYBLUE_BRIGHT = ("BG_SKYBLUE_BRIGHT", "106", {"background": "#00FFFF"})
    BG_WHITE_BRIGHT = ("BG_WHITE_BRIGHT", "107", {"background": "#FFFFFF"})


class ColorSchemeLight:
    BLACK = ("BLACK", "30", {"foreground": "#808080"})
    RED = ("RED", "31", {"foreground": "#FF8080"})
    GREEN = ("GREEN", "32", {"foreground": "#80FF80"})
    YELLOW = ("YELLOW", "33", {"foreground": "#FFFF80"})
    BLUE = ("BLUE", "34", {"foreground": "#8080FF"})
    PURPLE = ("PURPLE", "35", {"foreground": "#FF80FF"})
    SKYBLUE = ("SKYBLUE", "36", {"foreground": "#80FFFF"})
    WHITE = ("WHITE", "37", {"foreground": "#FFFFFF"})

    BG_BLACK = ("BG_BLACK", "40", {"background": "#808080"})
    BG_RED = ("BG_RED", "41", {"background": "#FF8080"})
    BG_GREEN = ("BG_GREEN", "42", {"background": "#80FF80"})
    BG_YELLOW = ("BG_YELLOW", "43", {"background": "#FFFF80"})
    BG_BLUE = ("BG_BLUE", "44", {"background": "#8080FF"})
    BG_PURPLE = ("BG_PURPLE", "45", {"background": "#FF80FF"})
    BG_SKYBLUE = ("BG_SKYBLUE", "46", {"background": "#80FFFF"})
    BG_WHITE = ("BG_WHITE", "47", {"background": "#FFFFFF"})

    BG_BLACK_BRIGHT = ("BG_BLACK_BRIGHT", "100", {"background": "#808080"})
    BG_RED_BRIGHT = ("BG_RED_BRIGHT", "101", {"background": "#FF8080"})
    BG_GREEN_BRIGHT = ("BG_GREEN_BRIGHT", "102", {"background": "#80FF80"})
    BG_YELLOW_BRIGHT = ("BG_YELLOW_BRIGHT", "103", {"background": "#FFFF80"})
    BG_BLUE_BRIGHT = ("BG_BLUE_BRIGHT", "104", {"background": "#8080FF"})
    BG_PURPLE_BRIGHT = ("BG_PURPLE_BRIGHT", "105", {"background": "#FF80FF"})
    BG_SKYBLUE_BRIGHT = ("BG_SKYBLUE_BRIGHT", "106", {"background": "#80FFFF"})
    BG_WHITE_BRIGHT = ("BG_WHITE_BRIGHT", "107", {"background": "#FFFFFF"})


class StyleScheme(StyleSchemeBase, FontScheme, ColorScheme):
    pass


class LightStyleScheme(StyleSchemeBase, FontScheme, ColorSchemeLight):
    pass


class LoggingHandler(Handler):
    END = "end"

    def __init__(self, box, scheme=None):
        super().__init__()
        self.box = box
        self.scheme = scheme or StyleScheme
        for style in self.scheme.to_dict().values():
            self.box.tag_config(style[0], **style[2])

    def emit(self, record: LogRecord) -> None:
        formated = self.format(record)
        splited = formated.split("\033[")
        self.box.insert(self.END, splited[0])
        tag = []
        for text in splited[1:]:
            codes = text.split("m", 1)[0].split(";")

            for code in codes:
                if code == "0":
                    tag = []
                else:
                    for style in self.scheme.to_dict().values():
                        if code == style[1]:
                            tag.append(style[0])
            self.box.insert(self.END, text.split("m", 1)[-1], tag)
        self.box.insert(self.END, "\n", tag)

        self.box.see(self.END)
        self.flush()
