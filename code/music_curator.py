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

@staticmethod
def ci_get_first(searchdict, searchkey, default):
    """
    This function returns the value of the first key in searchdict
    that matches the searchkey independent of its case, i.e. it. returns
    "The Beatles" when looking up in "ArTiSt: The Beatles" via "ARTIst".
    """
    all_keys = searchdict.keys()
    if searchkey.casefold() in [ key.casefold() for key in all_keys ]:
        for try_key in all_keys:
            if try_key.casefold() == searchkey.casefold():
                return searchdict[try_key]
    return default

class Track:
    def __init__(self, prefix, path):
        self.fullpath = prefix + '/' + path
        with open(self.fullpath) as tempFile:
            pass

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
            self.size = meta_info["size"]
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

    def pp_metadata(self):
        return json.dumps(self.metadata.__dict__, indent=2)

class TrackList:
    def __init__(self, listfilename, musicbase):
        self.listsource = listfilename
        self.totaltime = 0
        self.tracks = []
        with open(listfilename) as filelist:
            lines = filelist.readlines()
            totallines = len(lines)
            self.track_count = 0
            for line in lines:
                trackfilename = line.rstrip()
                # workaround for mpd/mpc bug when a ":" is part of the filename
                trackfilename = trackfilename.replace(u"\uf022", ":")
                track = Track(musicbase, trackfilename)
                track.detect_meta()
                self.tracks.append(track)
                self.track_count = self.track_count + 1
                self.totaltime = self.totaltime + track.duration_secs
                print ( f'done: {self.track_count:>6} of {totallines} ({self.track_count * 100 // totallines}%, last title: {track.title:{"_"}<30.30})', end='\r', file=sys.stderr)
            print ('\n', file=sys.stderr)

class LocalException(Exception):
    pass
