Metadata Specification
======================

Album metadata is provided as a nested :py:class:`dict` that contains information for the album, its tracks, and the player.

A simple example follows:

.. code-block:: python

    album = {
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
                "duration": 273,
                "lyrics": [
                    "Here is a stanza",
                    "And another stanza",
                    "",
                    "And this is the second verse",
                    "It's the first but worse"
                ],
                "about": "Here's a cat.\n\n![](https://placekitten.com/640/480)"
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
            "user_css": "fancypants.css",
            "footer_text": "Custom footer text"
        }
    }

Album
-----

The top-level :py:class:`dict` contains the following data:

* ``artist``: The recording artist's name
* ``title``: The title of the album
* ``artist_url``: The recording artist's homepage/website
* ``album_url``: The canonical web address for this album
* ``artwork``: The album-level artwork data
* ``tracks``: The individual tracks of this album
* ``theme``: Visual theme settings

Tracks
------

Track data is a :py:class:`list` of :py:class:`dict` of the following data
for each track:

* ``title``: The title of the track
* ``filename``: The preview audio file (optional)
* ``artwork``: Track-level artwork data
* ``explicit``: Whether this track contains explicit lyrics
* ``duration``: The length of the track (in seconds)
* ``lyrics``: The lyrics of the song, either as a big newline-separated
  string or as a :py:class:`list` of strings (one per line).
* ``about``: The extended information of the track, either as a
  newline-separated string or as a :py:class:`list` of strings (one per
  line). This text may be formatted with `markdown <https://commonmark.org/>`_.

Theme
-----

The visual theme settings are as follows:

* ``foreground``: Foreground text color
* ``background``: Background color
* ``highlight``: Highlight text color
* ``hide_footer``: Whether to hide the "Made with" footer
* ``user_css``: User CSS file to include, for deeper visual customization
* ``footer_text``: Custom HTML to override the "Made with" footer

Artwork
-------

Artwork data can be attached to an album and/or its tracks. It is a :py:class:`dict` with the following keys:

* ``1x``: The normal-DPI rendition of the thumbnail
* ``2x``: The high-DPI rendition of the thumbnail
* ``fullsize``: The fullsize rendition of the artwork

