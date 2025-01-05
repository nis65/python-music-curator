# HOWTO

## ffprobe binary
On debian/ubuntu systems this is part of the `ffmpeg` pkg, YMMV. Try if it is available on your `PATH`:

~~~
$ ffprobe -version | head -1
ffprobe version 4.4.2-0ubuntu0.22.04.1 Copyright (c) 2007-2021 the FFmpeg developers
~~~

## ffprobe3 python library

This is apparently not yet available as debian python pkg, so I just ripped off the `ffprobe3` directory from the [upstream source](https://github.com/jboy/ffprobe3-python3/tree/master/ffprobe3) and put it here.

This can be done better for sure.

## create a "playlist"

Other places call [m3u a file format](https://en.wikipedia.org/wiki/M3U), but basically it is just a list of filenames of audio files. I create it from my `mpd`instance with

~~~
mpc -h MYMPDHOST -f %file% playlist | tail -n +7  | head > songlist.txt
~~~

`mpd` lists all files relative to its own "root". And depending on the
environment I am working on, the same music library is available at
different mount points.

# adjust and run testcurate.py

To create a python `TrackList`, you need
* the path to the songlist (currently hardcoded to `songlist.txt` - yes, proper parameter handling is about to be implemented)
* the path to the music library that will be prepended to each filename in the songlist.

Check those two values, then run `testcurate.py`:

~~~
mp3   Take Five            Brubeck, Dave Quarte   51   326.15      5220480         44100  2 /home/nick/share/mp3-coll/sound/...
flac  With My Own Two Hand Ben Harper            100   274.69     32383821   2003  44100  2 /home/nick/share/mp3-coll/sound/...
...
list source songlist.txt has 10 tracks
total seconds 3233.755314, average song length 323.0
~~~

And this is it. For the moment.
