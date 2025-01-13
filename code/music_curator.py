"""
Track:

  identified by self.fullpath, pointing to an audio file

Track.detect_meta():

  analyzes audio file for meta information and sets it e.g. in Track.title

TrackList:

  A list of Tracks, identified by self.listsource. Some metadata (like total length) is kept.
  Currently, all tracks undergo .detect_meta() when creating a TrackList. Might change.

"""

import ffprobe3
import json
import re
import sys
from dateutil.parser import parse, ParserError
from datetime import timedelta

@staticmethod
def ci_get_first(searchdict, searchkey, default):
    """
    This function returns the value of the first key in searchdict
    that matches the searchkey independent of its case, i.e. it. returns
    "The Beatles" when looking up in "ArTiSt: The Beatles" via "ARTIst".
    """
    for try_key in searchdict.keys():
        if try_key.casefold() == searchkey.casefold():
            return searchdict[try_key]
    return default

@staticmethod
def pp_bytes(bytes):
    divisor=1000
    unitstrings = [ "B ", "KB" , "MB", "GB", "TB", "PB", "EB" ]
    unit = 0
    while bytes >= divisor and unit + 1 < len (unitstrings) :
        bytes, rest = divmod ( bytes, divisor)
        unit = unit + 1
    if unit == 0:
        return f"{int(bytes):>7} {unitstrings[0]}"
    else:
        return f"{int(bytes):>3}.{int(rest):{0}>3} {unitstrings[unit]}"

@staticmethod
def pp_seconds(seconds):
    isec, fsec = divmod(round(seconds*100), 100)
    try:
        result = f"{timedelta(seconds=isec)}.{fsec:02.0f}"
    except OverflowError:
        result = f"{seconds}s"
    return result

class Track:
    def __init__(self, prefix, path):
        self.fullpath = prefix + '/' + path
        with open(self.fullpath) as tempFile:
            pass

    def __str__(self):
        return f"title: {getattr(self, 'title', '-' )} artist: {getattr(self, 'artist', '-' )} fullpath: {self.fullpath}"

    def __repr__(self):
        return json.dumps(self, default=lambda x: x.__dict__)

    def pp(self):
        return f"""{self.codec:<5.5} {self.title:<20.20} {self.artist:<20.20} \
{self.probe_score:>4} \
{pp_seconds(self.duration_secs):>20.20} {pp_bytes(self.size):>10} {self.date:>6} \
{self.sample_rate:>6} {self.channels:>2} \
{self.fullpath}"""

    def detect_meta(self):
        probe = ffprobe3.probe(self.fullpath)
        if len(probe.audio) == 1:
            # audio info
            audio = probe.audio[0]
            self.sample_rate = audio["sample_rate"]
            self.channels = audio["channels"]
            self.channel_layout = audio.get("channel_layout", "nc")
            # meta info
            meta_info = probe.format.parsed_json
            self.codec = meta_info["format_name"]
            try:
                self.size = int(meta_info["size"])
            except SyntaxError:
                self.size = int(0)
            self.duration_secs = float(meta_info["duration"])
            self.probe_score = meta_info["probe_score"]
            # title, artist, date from tags (if possible)
            if meta_info.get("tags"):
                tag_title  = ci_get_first(meta_info["tags"], 'title' , 'nt')
                tag_artist = ci_get_first(meta_info["tags"], 'artist', 'na')
                tag_date   = ci_get_first(meta_info["tags"], 'date'  , '')
            else:
                tag_title = 'nt'
                tag_artist = 'na'
                tag_date = ''
            # compute title, artist from filename (maybe needed as last resort)
            # get filename without extension, replace '_' by ' '
            file_artist_title = re.sub(r'^.*/([^/]+)\.[^./]+$',
                                       r'\1', self.fullpath)
            file_artist_title = file_artist_title.replace('_', ' ')
            # assume that '-' is used to separate the artist
            # (coming first) from the title (coming last) in the
            # filename. If there are multiple '-', take the last
            # to be the separator
            if '-' in file_artist_title:
                file_artist, separator, file_title = file_artist_title.rpartition('-')
            else:
                file_title  = file_artist_title
                file_artist = 'na'
            # check title/artist tag values and use file values if not happy
            if tag_title == 'nt' or tag_artist == 'na':
                self.title = file_title.strip()
                self.artist = file_artist.strip()
            else:
                self.title = tag_title.strip()
                self.artist = tag_artist.strip()

            # finally, cleanup the date
            if tag_date != '':
                try:
                    timestamp = parse(tag_date, ignoretz=True)
                    intyear = int(timestamp.year)
                except ParserError:
                    intyear = 0
                if 1800 < intyear and intyear < 2100:
                    self.date = str(intyear)
                else:
                    self.date = f'{tag_date:>4.4}'
            else:
                self.date = ''
        else:
            raise LocalException(f'Not exactly 1 audio stream ({meta_info["nb_streams"]}) in {self.fullpath}');

class TrackList:
    def __init__(self, max_seconds=float(60*60*24*3600), max_size=512*1024*1024*1024):
        self.listsource = 'n/a'
        self.musicbase = 'n/a'
        self.max_seconds = float(max_seconds)
        self.max_size = int(max_size)
        self.tracks = []

    def detect_from_playlistfile(self, listfilename, musicbase):
        self.listsource = listfilename
        self.musicbase = musicbase
        with open(listfilename) as filelist:
            lines = filelist.readlines()
            # remove all comment lines
            lines = [ line for line in lines if not line.startswith('#') ]
            totallines = len(lines)
            track_count = 0
            for line in lines:
                trackfilename = line.rstrip()
                # workaround for mpd/mpc bug when a ":" is part of the filename
                trackfilename = trackfilename.replace(u"\uf022", ":")
                track = Track(musicbase, trackfilename)
                track.detect_meta()
                too_many_seconds = self.totaltime + track.duration_secs >= self.max_seconds
                too_many_bytes = self.totalsize + track.size >= self.max_size
                if too_many_seconds or too_many_bytes:
                    print()
                    print()
                    print(f'Stopped adding tracks at {track_count} of {totallines}, ')
                    if too_many_seconds:
                        print(f'new total time {pp_seconds(self.totaltime + track.duration_secs)} would exceed {pp_seconds(max_seconds)}')
                    if too_many_bytes:
                        print(f'new total size {pp_bytes(self.totalsize + track.size)} would exceed {pp_bytes(max_size)}')
                    break
                self.tracks.append(track)
                track_count = track_count + 1
                print ( f'done: {track_count:>6} of {totallines} ({track_count * 100 // totallines}%, last title: {track.title:{"_"}<30.30})', end='\r', file=sys.stderr)
            print ('\n', file=sys.stderr)

    @property
    def totaltime(self):
        sum = 0.0
        for track in self.tracks:
            sum = sum + track.duration_secs
        return sum

    @property
    def has_zero_time_tracks(self):
        for track in self.tracks:
            if track.duration_secs <= 0:
                return True
        return False

    @property
    def totalsize(self):
        sum = 0
        for track in self.tracks:
            sum = sum + track.size
        return sum

    @property
    def has_zero_size_tracks(self):
        for track in self.tracks:
            if track.size <= 0:
                return True
        return False

    @property
    def averagetime(self):
        if len(self.tracks) > 0:
            return self.totaltime / len(self.tracks)
        else:
            return 0

    @property
    def averagesize(self):
        if len(self.tracks) > 0:
            return self.totalsize / len(self.tracks)
        else:
            return 0

    def __repr__(self):
        return json.dumps(self, default=lambda x: x.__dict__)

    def __str__(self):
        return f"{self.listsource}: {len(self.tracks)} tracks, total time: {pp_seconds(self.totaltime)}, total bytes {pp_bytes(self.totalsize)}"

    def pp(self, with_tracks=True):
        output = f"{len(self.tracks)} tracks from {self.listsource} with base {self.musicbase}\n"
        output = output + f"  max  time/size: {pp_seconds(self.max_seconds)}/{pp_bytes(self.max_size)}\n"
        output = output + f"  zero time/size: {self.has_zero_time_tracks}/{self.has_zero_size_tracks}\n"
        if with_tracks:
            for track in self.tracks:
                output = output + f"    {track.pp()}\n"
            output = output + f"\n"
        else:
                output = output + f"    tracks hidden\n"
        output = output + f"  tot time/size: {pp_seconds(self.totaltime)}/{pp_bytes(self.totalsize)}\n"
        output = output + f"  avg time/size: {pp_seconds(self.averagetime)}/{pp_bytes(self.averagesize)}\n"
        return output

class LocalException(Exception):
    pass
