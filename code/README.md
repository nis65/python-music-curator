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
* the path to a playlist, e.g. `-p songlist.txt`
* the path to the music library that will be prepended to each filename in the songlist, e.g. `-m /my/mp3collection`

Run
~~~
./testcurate.py -p songlist.txt -m /home/nick/share/mp3-coll -d 1320 -s 43159994
~~~

These parameters are optional:

* `-d` is the maximum total duration of all songs allowed the playlist in seconds
* `-s` is the maximum total size of all files allowed on the playlist in bytes

When one (or both) maxima are reached, the `Tracklist.__init__`
functions stops adding tracks to the `Tracklist`.

~~~
$ ./testcurate.py -p songlist.txt -m /home/nick/share/mp3-coll -d 1320 -s 43159994
...
Stopped adding tracks at 3 of 10,
new total time 1532.315313 would exceed 1320.0
new total size 43159994 would exceed 43159994
...
mp3   Take Five            Brubeck, Dave Quarte   51   326.15      5220480         44100  2 /home/nick/share/mp3-coll/sound/...
flac  With My Own Two Hand Ben Harper            100   274.69     32383821   2003  44100  2 /home/nick/share/mp3-coll/sound/...
...
list generated from songlist.txt has 3 tracks
total seconds 1319.155313 (of 1320.0 allowed) average song length 439.71843766666666
total size 21111168 (of 43159994 allowed) average song size 7037056.0
good: All tracks have size > 0
good: All tracks have a duration > 0
~~~

And this is it. For the moment.
