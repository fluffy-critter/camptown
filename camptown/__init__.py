""" Build the Camptown player """

import logging
import os
import os.path
import typing

import jinja2
import mistune
from markupsafe import Markup, escape

try:
    from .__version__ import __version__
except ImportError:
    __version__ = '(unknown)'


LOGGER = logging.getLogger(__name__)

CAMPTOWN_URL = 'https://github.com/fluffy-critter/camptown'


def lyrics(text):
    """ Given lines of text, produce nice markup for lyrics """
    output = ''
    in_para = False
    if isinstance(text, str):
        lines = text.splitlines()
    elif isinstance(text, list):
        lines = text
    for line in lines:
        if line:
            if not in_para:
                output += Markup('<p class="verse">')
                in_para = True
            else:
                output += Markup('<br>')
            output += line
        else:
            if in_para:
                output += Markup('</p>')
                in_para = False
    if in_para:
        output += Markup('</p>')
    return output


class InfoRenderer(mistune.HTMLRenderer):
    """ Custom Markdown renderer for about boxes """

    def link(self, text, url, title=None):
        tag = f'<a href="{escape(url)}" target="_blank" rel="noopener"'
        if title:
            tag += f' title="{escape(url)}"'
        tag += '>'
        return f'{tag}{text}</a>'


def markdown(text):
    """ Given lines of text, convert as markdown """

    LOGGER.debug("text=%s  %s", type(text), text)

    if isinstance(text, list):
        text = '\n'.join(text)

    return Markup(mistune.create_markdown(renderer=InfoRenderer())(text))


def artwork_img(spec, **kwargs):
    """ Convert an artwork spec to an <img> tag """
    tag = '<img alt="" loading="lazy"'
    if '1x' in spec:
        tag += f' src="{escape(spec["1x"])}"'
    if '2x' in spec:
        tag += f' srcset="{escape(spec["1x"])} 1x, {escape(spec["2x"])} 2x"'

    for key, val in kwargs.items():
        tag += f' {escape(key)}="{escape(val)}"'

    tag += '>'
    return Markup(tag)


def seconds_timestamp(duration):
    """ Convert a duration (in seconds) to a timestamp like h:mm:ss """
    minutes, seconds = divmod(duration, 60)
    hours, minutes = divmod(minutes, 60)

    if hours:
        return f'{hours:.0f}:{minutes:02.0f}:{seconds:02.0f}'
    return f'{minutes:.0f}:{seconds:02.0f}'


def seconds_datetime(duration):
    """ Convert a duration (in seconds) to an HTML5 duration like 3h 5m 10s """
    minutes, seconds = divmod(duration, 60)
    hours, minutes = divmod(minutes, 60)

    if hours:
        return f'{hours:.0f}h {minutes:.0f}m {seconds:.0f}s'
    return f'{minutes:.0f}m {seconds:.0f}s'


def process(album, output_dir, footer_urls: typing.Optional[list[tuple[str, str]]] = None,
            **kwargs):
    """ Process an album into its output

    :param dict album: The album data
    :param str output_dir: Output directory to receive the output
    :param list[tuple[str,str]] footer_urls: A set of (url,text) for URLs to add
        to the page footer

    Album data is a :py:class:`dict` with the following keys and values:

    :param str artist: The recording artist's name
    :param str title: The title of the album
    :param str artist_url: The recording artist's homepage/website
    :param str album_url: The canonical web address for this album
    :param dict artwork: The album-level artwork data
    :param list[dict] tracks: The individual tracks of this album
    :param dict theme: Visual theme settings

    Artwork data is a :py:class:`dict` with the following keys:

    :param str 1x: The normal-DPI rendition of the thumbnail
    :param str 2x: The high-DPI rendition of the thumbnail
    :param str fullsize: The fullsize rendition of the artwork

    Track data is a :py:class:`list` of :py:class:`dict` of the following data
    for each track:

    :param str title: The title of the track
    :param str filename: The preview audio file (optional)
    :param dict artwork: Track-level artwork data
    :param bool explicit: Whether this track contains explicit lyrics
    :param int duration: The length of the track (in seconds)
    :param lyrics: The lyrics of the song, either as a big newline-separated
        string or as a :py:class:`list` of strings (one per line).
    :param about: The extended information of the track, either as a
        newline-separated string or as a :py:class:`list` of strings (one per
        line). This text may be formatted with `markdown <https://commonmark.org/>`_.

    The visual theme settings are as follows:

    :param str foreground: Foreground text color
    :param str background: Background color
    :param str highlight: Highlight text color
    :param bool hide_footer: Whether to hide the "Made with" footer
    :param str user_css: User CSS file to include, for deeper visual customization

    A simple example follows:

    .. code-block:: python

        camptown.process({
            "artist": "Sluggy Puppernutters",
            "title": "Self-Titled Album",

            "artist_url": "https://sluggy.example",
            "album_url": "https://sluggy.example/album/self-titled",

            "artwork": {
                "1x": "album-art-thumb.jpg",
                "2x": "album-art-hidpi.jpg",
                "fullsize": "album-art-fullsize.jpg"
            },

            "tracks": [
                {
                    "title": "Hit Single",
                    "filename": "hit single.mp3",
                    "artwork": {
                        "1x": "hit-single-thumb.jpg"
                    },
                    "explicit": True,
                    "duration": 273
                },
                {
                    "title": "We Hate Our Hit Single",
                    "filename": "something else.mp3",
                    "explicit": True,
                    "duration": 273
                },
                {
                    "title": "You'll have to buy the album to hear this one",
                    "duration": 3600
                }
            ],
            "theme": {
                "foreground": "white",
                "background": "black",
                "highlight": "yellow",
                "hide_footer": False,
                "user_css": "fancypants.css"
            }
        }, "my_album/preview")


    Note that this will *only* generate Camptown's own files into the specified
    directory; it is up to the caller to transcode/copy audio, images, and user CSS
    into the output directory. All path names are relative to `output_dir`.

    :returns: the list of generated files, relative to output_dir

    """

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
    env.filters['markdown'] = markdown
    env.filters['lyrics'] = lyrics
    env.filters['artwork_img'] = artwork_img
    env.filters['timestamp'] = seconds_timestamp
    env.filters['datetime'] = seconds_datetime

    outfiles = []

    urls = [(CAMPTOWN_URL, 'Camptown')]
    if footer_urls:
        urls += footer_urls

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
                                          **kwargs))
            outfiles.append(tmpl)

    return outfiles
