""" Module entry point """

import argparse
import json
import logging
import os
import os.path
import shutil

from . import __version__, process

LOG_LEVELS = [logging.WARNING, logging.INFO, logging.DEBUG]
LOGGER = logging.getLogger(__name__)


def main():
    """ Simple CLI for test purposes, mostly """

    parser = argparse.ArgumentParser("camptown")
    parser.add_argument("input_file", type=str, help="Album specfile")
    parser.add_argument("output_dir", type=str, help="Output directory")
    parser.add_argument("-v", "--verbosity", action="count",
                        help="Increase output logging level", default=0)
    parser.add_argument("--version", action="version",
                        version=f"%(prog)s {__version__}")

    args = parser.parse_args()
    logging.basicConfig(level=LOG_LEVELS[min(
        args.verbosity, len(LOG_LEVELS) - 1)],
        format='%(message)s')

    with open(args.input_file, 'r', encoding='utf-8') as file:
        album = json.load(file)
        LOGGER.info("Read %d tracks from %s", len(
            album['tracks']), args.input_file)

    input_dir = os.path.dirname(args.input_file)

    os.makedirs(args.output_dir, exist_ok=True)

    process(album, args.output_dir,
            file_callback=lambda path: os.path.join(input_dir, path))

    def copy_art(blob):
        if 'artwork' in blob:
            for key in ('1x', '2x', 'fullsize'):
                if key in blob['artwork']:
                    shutil.copy(os.path.join(input_dir, blob['artwork'][key]),
                                args.output_dir)

    copy_art(album)
    for track in album['tracks']:
        if 'filename' in track:
            shutil.copy(os.path.join(
                input_dir, track['filename']), args.output_dir)
        copy_art(track)

    theme = album.get('theme', {})
    if 'user_css' in theme:
        shutil.copy(os.path.join(
            input_dir, theme['user_css']), args.output_dir)

    LOGGER.info("Done")


if __name__ == '__main__':
    main()
