tag_wrapper
===========

Audio Tag Editing Code for Python. Developed for Oggify

===========

A simple front-end for mutagen, which abstracts away the format specific tag names and quirks.

This allows a tag object to be accessed as dictionaries with a single set of keys regardless of the actual keys used in
the format.

Ogg Vorbis tag names were used as the standard as they are human readable. Apple's m4a tags and ID3 tags are converted
on the fly to the correct field names.

For a list of supported fields in m4a or mp3 files, please look at their respective files.

For a usage example have a look at Oggify.
