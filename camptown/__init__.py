""" Build the Camptown player """
import collections
import functools
import logging
import os
import os.path
import re
import shutil
import typing
from urllib.parse import quote, urlparse

import jinja2
import mistune
import smartypants
from markupsafe import Markup, escape

try:
    from .__version__ import __version__
except ImportError:
    __version__ = '(unknown)'


LOGGER = logging.getLogger(__name__)

CAMPTOWN_URL = 'https://github.com/fluffy-critter/camptown'


FileCallback = typing.Callable[[str], str]


def slugify():
    """ Slugify a filename that maintains uniqueness in case of collision """
    counts: typing.Dict[str, int] = collections.defaultdict(lambda: 0)

    def _slugify(text):
        slug = re.sub(r'[^0-9a-zA-Z._]+', '-', text)
        count = counts[slug]
        counts[slug] += 1
        if count:
            slug += f'-{count}'
        return slug

    return _slugify


class InfoRenderer(mistune.HTMLRenderer):
    """ Custom Markdown renderer for about boxes """

    def __init__(self, output_dir, file_callback: typing.Optional[FileCallback],
                 outfiles: set[str]):
        super().__init__(escape=False)
        self.output_dir = output_dir
        self.file_callback = file_callback
        self.slugify = slugify()
        self.outfiles = outfiles
        self.map_cache: dict[str, str] = {}

    def link(self, text, url, title=None):
        LOGGER.debug("link text=%s url=%s title=%s", text, url, title)
        tag = f'<a href="{url}" target="_blank" rel="noopener"'
        if title:
            tag += f' title="{url}"'
        tag += '>'
        return f'{tag}{text}</a>'

    def map_url(self, url):
        """ Map a provided URL to an actual request URL """
        if url in self.map_cache:
            return self.map_cache[url]

        LOGGER.debug("got url %s", url)
        parsed = urlparse(url)
        if parsed.scheme:
            return url

        if not self.file_callback:
            raise RuntimeError(
                "Attempted to map a file, but no file_callback given")
        input_file = self.file_callback(parsed.path)
        basename = os.path.basename(input_file)
        name, ext = os.path.splitext(basename)
        output_file = self.slugify(f'image {name}')+ext
        shutil.copy(input_file, os.path.join(self.output_dir, output_file))
        self.outfiles.add(output_file)
        LOGGER.debug("added file %s", output_file)
        self.map_cache[url] = output_file
        return output_file

    def image(self, alt, url, title=None):  # pylint:disable=arguments-renamed
        LOGGER.debug("image alt=%s url=%s title=%s", alt, url, title)
        return super().image(alt, self.map_url(url), title)


def markdown(output_dir, file_callback, protections, linebreak):
    """ Given lines of text, convert as markdown """

    md_proc = mistune.create_markdown(
        renderer=InfoRenderer(output_dir, file_callback, protections),
        plugins=['strikethrough', 'table'])

    def _markdown(text):
        LOGGER.debug("text=%s  %s", type(text), text)

        if isinstance(text, list):
            text = linebreak.join(text)

        return Markup(smartypants.smartypants(md_proc(text)))
    return _markdown


def artwork_img(spec, **kwargs):
    """ Convert an artwork spec to an <img> tag """

    srcset = [f'{quote(filename)} {size}'
              for size, filename in spec.items()
              if isinstance(size, str)
              and isinstance(filename, str) and size[-1] == 'x']

    tag = '<img alt="" loading="lazy"'
    if '1x' in spec:
        tag += f' src="{quote(spec["1x"])}"'

    if 'width' in spec:
        tag += f' width={spec["width"]}'
    if 'height' in spec:
        tag += f' height={spec["height"]}'

    if srcset:
        tag += f' srcset="{", ".join(srcset)}"'

    if 'fullsize' in spec:
        tag += f' data-fullsize="{quote(spec["fullsize"])}"'

    for key, val in kwargs.items():
        tag += f' {escape(key)}="{escape(val)}"'

    tag += '>'
    return Markup(tag)


def seconds_timestamp(duration):
    """ Convert a duration (in seconds) to a timestamp like h:mm:ss """
    minutes, seconds = divmod(round(duration), 60)
    hours, minutes = divmod(minutes, 60)

    if hours:
        return f'{hours:.0f}:{minutes:02.0f}:{seconds:02.0f}'
    return f'{minutes:.0f}:{seconds:02.0f}'


def seconds_datetime(seconds):
    """ Convert a duration (in seconds) to an HTML5 duration like 3h 5m 10s """
    minutes, seconds = divmod(round(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    parts = [f'{val}{lbl}' for val, lbl in zip(
        [days, hours, minutes, seconds], 'dhms') if val > 0]
    return ' '.join(parts) if parts else '0s'


def process(album, output_dir,
            footer_urls: typing.Optional[list[tuple[str, str]]] = None,
            file_callback: typing.Optional[FileCallback] = None) -> set[str]:
    """ Process an album into its output

    :param dict album: The album data
    :param str output_dir: Output directory to receive the output
    :param list[tuple[str,str]] footer_urls: A set of (url,text) for URLs to add
        to the page footer
    :param callable file_request_callback: A callback to handle file requests;
        takes one parameters source_filename, and returns the path to the
        requested file.

    See :doc:`the metadata specification <metadata>` for how to fill out the album data.

    Note that this will *only* generate Camptown's own files into the specified
    directory; it is up to the caller to transcode/copy audio, images, and user CSS
    into the output directory. All path names are relative to `output_dir`.

    :returns: the set of generated files, relative to output_dir

    """

    outfiles: set[str] = set()

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join(
            os.path.dirname(__file__), 'templates')),
        autoescape=True)
    env.filters['markdown'] = markdown(
        output_dir, file_callback, outfiles, '\n')
    env.filters['lyrics'] = markdown(
        output_dir, file_callback, outfiles, '  \n')
    env.filters['artwork_img'] = artwork_img
    env.filters['timestamp'] = seconds_timestamp
    env.filters['datetime'] = seconds_datetime

    if 'theme' in album and 'footer_text' in album['theme']:
        footer_text = Markup(album['theme']['footer_text'])
    else:
        urls = footer_urls or [(CAMPTOWN_URL, 'Camptown')]

        footer_text = Markup("Made with " + ' + '.join([
            f'<a href="{url}" target="_blank" rel="noopener">{text}</a>'
            for url, text in urls]))

    for tmpl in ('index.html', 'player.js', 'player.css'):
        LOGGER.info("Writing %s", tmpl)
        template = env.get_template(tmpl)
        with open(os.path.join(output_dir, tmpl), 'w', encoding='utf8') as outfile:
            outfile.write(template.render(album=album,
                                          theme=album.get('theme', {}),
                                          tracks=album.get('tracks', []),
                                          footer_text=footer_text,
                                          version=__version__,
                                          ))
            outfiles.add(tmpl)

    return outfiles
