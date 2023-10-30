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



def process(album, output_dir, footer_urls:typing.Optional[list[tuple[str,str]]]=None,
    **kwargs):
    """ Process an album into its output

    :param dict album: The album data
    :param str output_dir: Output directory to receive the output
    :param list[tuple[str,str]] footer_urls: A set of (url,text) for URLs to add
        to the page footer

    See :doc:`the metadata specification <metadata>` for how to fill out the album data.

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
        for url,text in urls]))

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


