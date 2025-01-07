#!/usr/bin/python3

import music_curator as mc
import argparse


parser = argparse.ArgumentParser(
                    prog=__file__,
                    description='Do some tests with the music_curator',
                    epilog='Have fun!')
parser.add_argument('-p', '--playlist')
parser.add_argument('-m', '--musicbase')
parser.add_argument('-s', '--size')
parser.add_argument('-d', '--duration')

args = parser.parse_args()

if args.playlist:
    inputplaylist = args.playlist
else:
    inputplaylist = 'songlist.txt'

if args.musicbase:
    musicbase = args.musicbase
else:
    musicbase = '/home/nick/share/mp3-coll'

if args.size:
    maxsize = int(args.size)
else:
    maxsize = 512 * 1024 * 1024 * 1024

if args.duration:
    maxduration = float(args.duration)
else:
    maxduration = float(60 * 60 * 24 * 365 * 10)

print (f'analyzing playlist "{inputplaylist}" and searching music in "{musicbase}"')
print (f'maxsize "{maxsize}" maxduration "{maxduration}"')
print ()

# create track list with
# mpc -h wohnen -f %file% playlist | tail -n +7  | head > songlist.txt

# album = mc.TrackList(inputplaylist, musicbase, 60*30)
# album = mc.TrackList(inputplaylist, musicbase, max_size=43159994)
album = mc.TrackList(inputplaylist, musicbase, max_seconds=maxduration, max_size=maxsize)

for track in album.tracks:
    print(f"{track.codec:<5.5} {track.title:<20.20} {track.artist:<20.20} "
          f"{track.probe_score:>4} "
          f"{track.duration_secs:>8.2f} {track.size:>12} {track.date:>6} "
          f"{track.sample_rate:>6} {track.channels:>2} "
          f"{track.fullpath}")

print ()
print (f'list generated from {album.listsource} has {len(album.tracks)} tracks')
print (f'total seconds {album.totaltime} (of {album.max_seconds} allowed) average song length {album.averagetime}')
print (f'total size {album.totalsize} (of {album.max_size} allowed) average song size {album.averagesize}')
print (f'total minimal size on disk {album.totalsize}')
if album.has_zero_size_tracks:
    print ('Warning: Some tracks have size 0')
else:
    print ('good: All tracks have size > 0')
if album.has_zero_time_tracks:
    print ('Warning: Some tracks have no duration')
else:
    print ('good: All tracks have a duration > 0')
