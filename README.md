# python-music-curator

This is (i.e. should become) a collection of python scripts helping me
to curate my large (>900GB) audio collection.

Goals:

* learn python
* make my audio library better

## Use cases

**import** into the library:

* rip from an audio cd
  * lookup metadata in cddb
  * review / manually fix metadata
  * convert to nicely tagged `flac` files
  * push into library
* buy from bandcamp
  * review / manually fix metadata
  * convert `wav` to `flac`, no resampling, no lossy de/compression
  * push into library

**manage** library:

* remove duplicates (e.g. mp3 and wav)
* improve tags

**export** from library:

* burn an audio cd from a track list
  * convert to wav
  * create cdrdao cuesheet for cd text (with title/artist)
  * create cdlabel (#, time, title, artist)

## Architecture

Two objects so far:

* a **Track** points to the audio file and is meant to contain all Meta Information in a unified way (it is always `title`, not sometimes `tracktitle` or `TITLE`.
  * meta info of a Track can be autodectect from the audio file with the `detect_meta()` method. The heavy lifting is done by `ffprobe3`.

* a **TrackList** is a list of **Track**s with some meta information for the List itself.
  * the Tracklist points to an `.m3u` file (just a list of absolute filenames)
  * a Tracklist can also be a "master" for an audio CD: As long as the total length of audio does not exceed the cdrom media capacity, all information needed to burn an audio CD are there.

## Background

This is my first python code written from scratch. Bare with me.
