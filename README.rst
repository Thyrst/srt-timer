srt-timer
=========

srt-timer simply converts subtitles from one timing to another one.

Usage example
-------------

You downloaded Fear the Walking Dead, episode 03x06, version 720p.WEB-DL-RARBG and
you want to have an Italian subtitles. However Italian subtitles are just
for the version REPACK.SVA...

Now you can simply use srt-timer for convert the subtitles to the wanted version.
First, you have to download English subtitles in both REPACK.SVA and 720p.WEB-DL-RARBG
and then you can create repack2webdl.sdiff file with conversion information:

.. code-block:: bash

    $ srt_timer.py make_sdiff --strip-original 11 \
    > "Fear the Walking Dead - 03x06 - Red Dirt.REPACK.SVA.English.C.orig.Addic7ed.com.srt" \
    > "Fear the Walking Dead - 03x06 - Red Dirt.WEB-DL RARBG.English.C.orig.Addic7ed.com.srt" \
    > --output repack2webdl.sdiff


``strip-original`` argument removes the preview subtitles that shouldn't be in the final version.

Now you convert your Italian subtitles to 720p.WEB-DL-RARBG version with the created sdiff file:

.. code-block:: bash

    $ srt_timer.py convert --sdiff repack2webdl.sdiff \
    > "Fear the Walking Dead - 03x06 - Red Dirt.REPACK.SVA.Italian.C.orig.Addic7ed.com.srt" \
    > --output italian_webdl.srt


And you're done.

Installation
------------

The package is on Pypi, so you can install it simply with ``pip install srt-timer``

Usage manual
------------

For help just type ``srt_timer.py --help`` or ``srt_timer.py [command] --help``

convert
^^^^^^^

Convert srt file from one timing to another one.

You can use it with a sdiff file like in the usage example or you can
convert subtitles directly by providing ``original-timing`` and ``new-timing``
arguments instead of ``sdiff`` argument. In the second case you can also
provide the ``strip-original`` argument to strip surplus subtitles on the beginning
of a file.

The result is printed to the standard output by default. If you define the ``output``
argument, then it's printed to a specified file.

make_sdiff
^^^^^^^^^^

Creates a sdiff file.

It has two required arguments: srt file with original timing and srt file with wanted timing.
Optional arguments are ``strip-original`` and ``output``.

The ``strip-original`` argument should be number of the last subtitle
in the "You've seen previously..." section if it isn't desired in a new subtitle version.
If defined, it will trim all subtitles starting before or at the time of the provided subtitle.

Same as for the ``convert`` command, the result is printed to the standard output
if you don't define an ``output`` argument.

Need help?
----------

If you have trouble using srt-timer, make a new issue on
`the GitHub page of the project <https://github.com/Thyrst/srt-timer>`_
or mail me at ``thyrst@seznam.cz``
