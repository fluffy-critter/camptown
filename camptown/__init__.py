""" Build the Camptown player """

import logging
import os
import os.path

import jinja2
import mistune
from markupsafe import Markup, escape

try:
    from .__version__ import __version__
except ImportError:
    __version__ = '(unknown)'


LOGGER = logging.getLogger(__name__)


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

    LOGGER.debug("text=%s  %s", type(text), text)

    return Markup(mistune.create_markdown(renderer=InfoRenderer())(text))

def artwork_img(spec, **kwargs):
    """ Convert an artwork spec to an <img> tag """
    tag = f'<img alt="" src="{escape(spec["1x"])}" loading="lazy"'
    if 'width' in spec:
        tag += f' width="{escape(spec["width"])}"'
    if 'height' in spec:
        tag += f' height="{escape(spec["height"])}"'
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



def process(album, output_dir):
    """ Process an album into its output

    :param dict album: The album data
    :param str output_dir: Output directory to receive the output

    Album data is formatted like:

    .. code-block:: python

        album = {
            "artist": "The album artist",
            "title": "The title of the album",
            "artwork": {                            # optional
                "width": 300,                       # optional
                "height": 300,                      # optional
                "1x": "image-300x300.jpg",
                "2x": "image-600x600.jpg"           # optional
            },
            "tracks": [
                {
                    "title": "The title of the track",
                    "filename": "audio file.mp3",   # optional - won't get a player if missing
                    "artwork": {                    # optional - overrides the album artwork
                        "width": 300,               # optional
                        "height": 300,              # optional
                        "1x": "image-300x300.jpg",
                        "2x": "image-600x600.jpg"   # optional
                    },
                    "explicit": True                # optional
                    "duration": 273                 # optional, time in seconds
                }
            ]
        }

    """

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
    env.filters['markdown'] = markdown
    env.filters['lyrics'] = lyrics
    env.filters['artwork_img'] = artwork_img
    env.filters['timestamp'] = seconds_timestamp
    env.filters['datetime'] = seconds_datetime

    for tmpl in ('index.html', 'player.js', 'player.css'):
        LOGGER.info("Writing %s", tmpl)
        template = env.get_template(tmpl)
        with open(os.path.join(output_dir, tmpl), 'w', encoding='utf8') as outfile:
            LOGGER.debug("generating %s", tmpl)
            outfile.write(template.render(album=album))
