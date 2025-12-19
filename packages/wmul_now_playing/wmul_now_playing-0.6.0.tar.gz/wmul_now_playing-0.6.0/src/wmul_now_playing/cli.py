"""
@Author = 'Mike Stanley'

Describe this file.

============ Change Log ============
8/15/2018 = Created.

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
import click
import multiprocessing
import wmul_logger
from wmul_now_playing import settings, display
from wmul_rivendell_tcp_client import receiver

_logger = wmul_logger.get_logger()


@click.command()
@click.argument("page_design", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.option("--host", type=str, help="The hostname or ip address of the now playing host.")
@click.option("--port", type=int, help="The port number for the now playing host.")
@click.option('--log_name', type=click.Path(exists=False, file_okay=True, dir_okay=False, writable=True),
              default=None,required=False, help="The path to the log file for the tcp process.")
@click.option('--log_level', type=click.IntRange(10,50, clamp=True), required=False, default=30,
              help="The log level: 10: Debug, 20: Info, 25: Verbose, 30: Warning, 40: Error, 50: Critical. "
                   "Intermediate values (E.G. 32) are permitted, but will essentially be rounded up (E.G. Entering 32 "
                   "is the same as entering 40. Logging messages lower than the log level will not be written to the "
                   "log. E.G. If 30 is input, then all Debug, Info, and Verbose messages will be silenced.")
def wmul_now_playing_cli(page_design, host, port, log_name, log_level):
    global _logger
    logging_queue = multiprocessing.Queue()
    stop_logger = wmul_logger.run_queue_listener_logger(
        logging_queue=logging_queue,
        file_name=log_name,
        log_level=log_level
    )
    _logger = wmul_logger.get_queue_handler_logger(logging_queue=logging_queue)

    _logger.debug("In command_line_interface")

    quit_event = multiprocessing.Event()
    song_queue = multiprocessing.SimpleQueue()
    if host and port:
        dss = receiver.DeviceServerSettings(
            host=host,
            port=port
        )
        tcp_process = multiprocessing.Process(
            target=receiver.connect_to_rivendell_tcp,
            name="Rivendell TCP Client",
            kwargs={
                "device_server_settings": dss,
                "quit_event": quit_event,
                "song_queue": song_queue,
                "loggging_queue": logging_queue
            },
            daemon=True
        )
        _logger.info("Spinning up TCP process.")
        tcp_process.start()

    pd = settings.PageDesign.load_from_file(page_design)
    display.run_display(page_design=pd, quit_event=quit_event, song_queue=song_queue, logging_queue=logging_queue)
