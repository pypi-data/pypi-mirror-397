"""
@Author = 'Mike Stanley'

Describe this file.

============ Change Log ============
7/19/2018 = Created.

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
import abc
import pygame
import wmul_logger
import sys
from functools import total_ordering
from queue import Empty as QueueEmpty
from wmul_now_playing import settings

_logger = wmul_logger.get_logger()


@total_ordering
class PyGameBase(abc.ABC):

    def __init__(self, item_settings, screen):
        self.item_settings = item_settings
        self.screen = screen

    def __eq__(self, other):
        return self.item_settings.order == other.item_settings.order

    def __lt__(self, other):
        return self.item_settings.order < other.item_settings.order

    @abc.abstractmethod
    def draw(self):
        pass


class PyGameText(PyGameBase):

    def __init__(self, item_settings, screen):
        super().__init__(item_settings=item_settings, screen=screen)
        font_filename = pygame.font.match_font(item_settings.font_names, bold=item_settings.bold)
        self.font = pygame.font.Font(font_filename, item_settings.font_size)
        self.rendered_font = self.create_rendered_font()

    def create_rendered_font(self):
        return self.font.render(
            self.item_settings.text,
            0,
            self.item_settings.fg_color.to_tuple()
        )

    def draw(self):
        self.screen.blit(self.rendered_font, (self.item_settings.x, self.item_settings.y))


class PyGameDynamicText(PyGameText):

    def __init__(self, item_settings, screen):
        super().__init__(item_settings=item_settings, screen=screen)

    @property
    def max_width(self):
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        left_margin = self.item_settings.x
        margin_width = left_margin + self.item_settings.margin_right
        return screen_width - margin_width

    def update_text(self, new_text):
        text_fits = False
        while not text_fits:
            self.item_settings.update_text(new_text=new_text)
            font_width, _ = self.font.size(self.item_settings.text)
            if font_width <= self.max_width:
                text_fits = True
            else:
                new_text = new_text[:-1]
        self.rendered_font = self.create_rendered_font()

    def reset_to_default_text(self):
        self.item_settings.reset_to_default_text()
        self.rendered_font = self.create_rendered_font()


class PyGameDummyDynamicText:

    def __init__(self):
        pass

    def update_text(self, new_text):
        pass

    def reset_to_default_text(self):
        pass

    def draw(self):
        pass


class PyGameImage(PyGameBase):

    def __init__(self, item_settings, screen):
        super().__init__(item_settings=item_settings, screen=screen)
        self.image = pygame.image.load(item_settings.path)
        self.image_rect = self.image.get_rect()
        self.image_rect.x = item_settings.x
        self.image_rect.y = item_settings.y

    def draw(self):
        self.screen.blit(self.image, self.image_rect)


class PyGameBox(PyGameBase):

    def __init__(self, item_settings, screen):
        super().__init__(item_settings=item_settings, screen=screen)
        self.rect = pygame.Rect(item_settings.x, item_settings.y, item_settings.width, item_settings.height)

    def draw(self):
        self.screen.fill(color=self.item_settings.bg_color.to_tuple(), rect=self.rect)


class _PyGameNowPlayingWindow:

    def __init__(self, page_design, song_queue, quit_event):
        _logger.info(f"In _PygameNowPlayingWindow with {page_design}")
        self.screen = self.create_screen(page_design=page_design)
        pygame.display.set_caption(page_design.display_settings.caption)
        self.drawables, self.artist_field, self.title_field = _create_page_elements(
            page_elements=page_design.page_elements,
            screen=self.screen
        )
        try:
            pygame.mouse.set_visible(False)
        except pygame.error:
            pass
        self.page_design = page_design
        self.song_queue = song_queue
        self.SONG_OVER_EVENT_ID = pygame.USEREVENT + 1
        self.quit_event = quit_event
        self.current_song = None
        self.clock = pygame.time.Clock()

    def create_screen(self, page_design):
        if page_design.display_settings.full_screen:
            display_flags = pygame.FULLSCREEN | pygame.NOFRAME
        else:
            display_flags = 0
        return pygame.display.set_mode(
            (page_design.display_settings.screen_width, page_design.display_settings.screen_height),
            display_flags
        )

    def update_artist_and_title(self):
        if self.current_song:
            self.artist_field.update_text(self.current_song.artist)
            self.title_field.update_text(self.current_song.title)
        else:
            self.artist_field.reset_to_default_text()
            self.title_field.reset_to_default_text()

    def update_song(self):
        if self.page_design.display_settings.song_update_mode == settings.SongUpdateMode.Static:
            return
        this_song = None
        while not self.song_queue.empty():
            try:
                this_song = self.song_queue.get()
            except QueueEmpty as qe:
                pass
        if this_song:
            self.current_song = this_song
            self.update_artist_and_title()
            pygame.time.set_timer(self.SONG_OVER_EVENT_ID, 0)
            duration_in_seconds = this_song.duration.total_seconds() \
                                  + self.page_design.display_settings.song_over_padding_seconds
            pygame.time.set_timer(self.SONG_OVER_EVENT_ID, int(duration_in_seconds) * 1000)

    def song_over(self):
        pygame.time.set_timer(self.SONG_OVER_EVENT_ID, 0)
        self.current_song = None
        self.update_artist_and_title()

    def end_program(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def check_events(self):
        if self.quit_event.is_set():
            _logger.debug("Quit Event is set")
            self.end_program()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                _logger.debug("PyGame Quit")
                self.quit_event.set()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if (pygame.key.get_mods() and pygame.KMOD_CTRL) == pygame.KMOD_CTRL:
                    if event.key == pygame.K_c:
                        _logger.debug("Control C pressed")
                        self.end_program()
            elif event.type == self.SONG_OVER_EVENT_ID:
                self.song_over()

    def update_screen(self):
        self.screen.fill(self.page_design.display_settings.bg_color.to_tuple())
        for element in self.drawables:
            element.draw()
        pygame.display.flip()

    def check_for_updated_config_file(self):
        new_page = self.page_design.check_for_updated_config_file()
        if new_page:
            _logger.debug("New config file found.")
            self.screen = self.create_screen(page_design=new_page)
            self.page_design = new_page
            self.drawables, self.artist_field, self.title_field = \
                _create_page_elements(new_page.page_elements, self.screen)
            if self.page_design.display_settings.song_update_mode == settings.SongUpdateMode.Dynamic:
                self.update_artist_and_title()
            else:
                self.song_over()
            pygame.display.set_caption(new_page.display_settings.caption)

    def loop(self):
        while True:
            self.check_events()
            self.check_for_updated_config_file()
            self.update_song()
            self.update_screen()
            self.clock.tick(5)


def _create_page_elements(page_elements, screen):
    elements = []
    artist_field = PyGameDummyDynamicText()
    title_field = PyGameDummyDynamicText()
    for elem in page_elements:
        elem_type = type(elem)
        if elem_type == settings.TextField:
            pygame_item = PyGameText(item_settings=elem, screen=screen)
        elif elem_type == settings.BoxField:
            pygame_item = PyGameBox(item_settings=elem, screen=screen)
        elif elem_type == settings.ImageField:
            try:
                pygame_item = PyGameImage(item_settings=elem, screen=screen)
            except FileNotFoundError as fnf:
                _logger.error(fnf)
                continue
        elif elem_type == settings.DynamicTextField:
            pygame_item = PyGameDynamicText(item_settings=elem, screen=screen)
            if elem.field_type == settings.DynamicFieldType.Artist:
                artist_field = pygame_item
            elif elem.field_type == settings.DynamicFieldType.Title:
                title_field = pygame_item
        else:
            raise TypeError
        elements.append(pygame_item)
    elements.sort()
    return elements, artist_field, title_field


def run_display(page_design, song_queue, quit_event, logging_queue):
    global _logger
    _logger = wmul_logger.get_queue_handler_logger(logging_queue=logging_queue)
    _logger.debug("In run_display.")
    try:
        pygame.init()
        np = _PyGameNowPlayingWindow(page_design=page_design, song_queue=song_queue, quit_event=quit_event)
        np.loop()
    except Exception as e:
        quit_event.set()
        _logger.error(e)
        raise
