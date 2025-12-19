"""
@Author = 'Mike Stanley'

Describe this file.

============ Change Log ============
7/20/2018 = Created.

============ License ============
MIT License

Copyright (c) 2018, 2025 Mike Stanley

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import configparser
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import total_ordering
from pathlib import Path
import wmul_logger


_logger = wmul_logger.get_logger()


class NowPlayingConfigParser(configparser.ConfigParser):

    def getcolor(self, section, option, *, raw=False, vars=None, fallback=configparser._UNSET, **kwargs):
        return self._get_conv(section, option, ColorField.from_csv_string,
                              raw=raw, vars=vars, fallback=fallback, **kwargs)

    def getsongupdatemode(self, section, option, *, raw=False, vars=None, fallback=configparser._UNSET, **kwargs):
        return self._get_conv(section, option, SongUpdateMode.from_string,
                              raw=raw, vars=vars, fallback=fallback, **kwargs)

    def getdynamicfieldtype(self, section, option, *, raw=False, vars=None, fallback=configparser._UNSET, **kwargs):
        return self._get_conv(section, option, DynamicFieldType.from_string,
                              raw=raw, vars=vars, fallback=fallback, **kwargs)


class SongUpdateMode(Enum):
    Static = auto()
    Dynamic = auto()

    def __str__(self):
        return self.name

    @classmethod
    def from_string(cls, input_string):
        try:
            return cls[input_string.title()]
        except KeyError:
            return cls.Static


class DynamicFieldType(Enum):
    Artist = auto()
    Title = auto()

    def __str__(self):
        return self.name

    @classmethod
    def from_string(cls, input_string):
        return cls[input_string.title()]


@dataclass
class ColorField:
    red: int = 0
    green: int = 0
    blue: int = 0

    def __str__(self):
        return f"ColorField: {self.red}, {self.green}, {self.blue}"

    def to_tuple(self):
        return self.red, self.green, self.blue

    @classmethod
    def from_csv_string(cls, config_string):
        r, g, b = config_string.split(",")
        r = int(r)
        g = int(g)
        b = int(b)
        return cls(r, g, b)

    def to_csv_string(self):
        return f"{self.red}, {self.green}, {self.blue}"


@dataclass
class ConfigFileInfo:
    config_file: Path
    config_file_mtime: int

    def check_for_updated_config_file(self):
        try:
            mtime = self.config_file.stat().st_mtime
        except FileNotFoundError as fnf:
            mtime = -1

        return mtime > self.config_file_mtime


@dataclass
class DisplaySettings:
    caption: str = "Now Playing"
    screen_width: int = 1280
    screen_height: int = 720
    song_update_mode: SongUpdateMode = SongUpdateMode.Static
    song_over_padding_seconds: int = 2
    full_screen: bool = False
    bg_color: ColorField = field(default_factory=ColorField)

    @classmethod
    def load_from_config_dict(cls, config_dict):
        screen_width = config_dict.getint("ScreenWidth", 1280)
        screen_height = config_dict.getint("ScreenHeight", 720)
        caption = config_dict.get("Caption", "Now Playing")
        song_update_mode = config_dict.getsongupdatemode("SongUpdateMode", SongUpdateMode.Static)
        song_over_padding_seconds = config_dict.getint("SongOverPadding", 0)
        full_screen = config_dict.getboolean("Full_Screen", False)
        bg_color = config_dict.getcolor("BG_Color", ColorField)

        return cls(screen_width=screen_width, screen_height=screen_height, caption=caption,
                   song_update_mode=song_update_mode, song_over_padding_seconds=song_over_padding_seconds,
                   full_screen=full_screen, bg_color=bg_color)


@dataclass
class PageDesign:
    display_settings: DisplaySettings
    page_elements: list
    page_file_info: ConfigFileInfo

    def check_for_updated_config_file(self):
        if self.page_file_info.check_for_updated_config_file():
            new_design = PageDesign.load_from_file(str(self.page_file_info.config_file))
            return new_design.verify()
        else:
            return False

    def verify(self):
        if not self.display_settings:
            return False
        if not self.page_elements:
            return False
        return self

    @classmethod
    def load_from_file(cls, page_file_name):
        _logger.debug(f"In PageDesign.load_from_file with {page_file_name}")
        config = NowPlayingConfigParser()
        config.read(page_file_name)
        config_path = Path(page_file_name)
        mtime = config_path.stat().st_mtime
        _logger.info(f"File has mtime: {str(mtime)}")
        page_file_info = ConfigFileInfo(config_file=config_path, config_file_mtime=mtime)

        display_settings = None
        page_elements = []

        _logger.info("Iterating the config.")
        for key in config:
            _logger.info(f"Working on {key}")
            hide = config[key].getboolean("Hide", False)
            if hide:
                _logger.info("Is hidden.")
                continue
            field_type = config[key].get("Type", "").casefold()
            if field_type == "display":
                _logger.info("Is display.")
                display_settings = DisplaySettings.load_from_config_dict(config[key])
            elif field_type == "text":
                _logger.info("Is text.")
                this_field = TextField.load_from_config_dict(config[key])
                page_elements.append(this_field)
            elif field_type == "dynamictext":
                _logger.info("Is dynamic text.")
                this_field = DynamicTextField.load_from_config_dict(config[key])
                page_elements.append(this_field)
            elif field_type == "image":
                _logger.info("Is image.")
                this_field = ImageField.load_from_config_dict(config[key])
                page_elements.append(this_field)
            elif field_type == "box":
                _logger.info("Is box.")
                this_field = BoxField.load_from_config_dict(config[key])
                page_elements.append(this_field)

        return cls(display_settings=display_settings, page_elements=page_elements, page_file_info=page_file_info)


@total_ordering
@dataclass(eq=False)
class OrderedField:
    order: int
    x: int
    y: int

    def __eq__(self, other):
        if isinstance(other, OrderedField):
            return self.order == other.order
        raise NotImplemented

    def __lt__(self, other):
        if isinstance(other, OrderedField):
            return self.order < other.order
        raise NotImplemented


@dataclass(eq=False)
class TextField(OrderedField):
    font_names: str
    font_size: int
    bold: bool
    text: str
    fg_color: ColorField
    bg_color: ColorField

    @classmethod
    def load_from_config_dict(cls, config_dict):
        order = config_dict.getint("Order")
        x = config_dict.getint("X")
        y = config_dict.getint("Y")
        fonts = config_dict.get("Fonts")
        font_size = config_dict.getint("FontSize")
        bold = config_dict.getboolean("BOLD")
        text = config_dict.get("Text")
        fg_color = config_dict.getcolor("FG_Color")
        bg_color = config_dict.getcolor("BG_Color")

        return cls(
            order=order,
            x=x,
            y=y,
            font_names=fonts,
            font_size=font_size,
            bold=bold,
            text=text,
            fg_color=fg_color,
            bg_color=bg_color
        )


@dataclass(eq=False)
class DynamicTextField(TextField):
    prefix: str
    suffix: str
    margin_right: int
    field_type: DynamicFieldType

    def __post_init__(self):
        self.default_text = self.text
        self.reset_to_default_text()

    def update_text(self, new_text):
        self.text = " ".join([self.prefix, new_text, self.suffix])

    def reset_to_default_text(self):
        self.update_text(self.default_text)

    @classmethod
    def load_from_config_dict(cls, config_dict):
        order = config_dict.getint("Order")
        x = config_dict.getint("X")
        y = config_dict.getint("Y")
        fonts = config_dict.get("Fonts")
        font_size = config_dict.getint("FontSize")
        bold = config_dict.getboolean("BOLD")
        text = config_dict.get("Text")
        fg_color = config_dict.getcolor("FG_Color")
        bg_color = config_dict.getcolor("BG_Color")
        prefix = config_dict.get("PreFix", "")
        suffix = config_dict.get("Suffix", "")
        margin_right = config_dict.getint("Margin_Right", 0)
        field_type = config_dict.getdynamicfieldtype("Field_Type")

        return cls(
            order=order,
            x=x,
            y=y,
            font_names=fonts,
            font_size=font_size,
            bold=bold,
            text=text,
            fg_color=fg_color,
            bg_color=bg_color,
            prefix=prefix,
            suffix=suffix,
            margin_right=margin_right,
            field_type=field_type,
        )


@dataclass(eq=False)
class ImageField(OrderedField):
    path: str
    scale: float

    @classmethod
    def load_from_config_dict(cls, config_dict):
        order = config_dict.getint("Order")
        x = config_dict.getint("X")
        y = config_dict.getint("Y")
        img_path = config_dict.get("Path")
        scale = config_dict.getfloat("Scale")
        scale = scale / 100  # Convert percent to decimal.

        return cls(
            order=order,
            x=x,
            y=y,
            path=img_path,
            scale=scale
        )


@dataclass(eq=False)
class BoxField(OrderedField):
    width: int = 500
    height: int = 300
    bg_color: ColorField = field(default_factory=ColorField)

    @classmethod
    def load_from_config_dict(cls, config_dict):
        order = config_dict.getint("Order")
        x = config_dict.getint("X")
        y = config_dict.getint("Y")
        bg_color = config_dict.getcolor("BG_Color", ColorField())
        width = config_dict.getint("Width")
        height = config_dict.getint("Height")

        return cls(
            order=order,
            x=x,
            y=y,
            width=width,
            height=height,
            bg_color=bg_color
        )
