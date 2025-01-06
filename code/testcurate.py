#!/usr/bin/python3

import music_curator as mc
import argparse


parser = argparse.ArgumentParser(
                    prog=__file__,
                    description='Do some tests with the music_curator',
                    epilog='Have fun!')
parser.add_argument('-p', '--playlist')
parser.add_argument('-m', '--musicbase')

args = parser.parse_args()

if args.playlist:
    inputplaylist = args.playlist
else:
    inputplaylist = 'songlist.txt'

if args.musicbase:
    musicbase = args.musicbase
else:
    musicbase = '/home/nick/share/mp3-coll'

print (f'analyzing playlist "{inputplaylist}" and searching music in "{musicbase}"')
print ()

# create track list with
# mpc -h wohnen -f %file% playlist | tail -n +7  | head > songlist.txt

album = mc.TrackList(inputplaylist, musicbase)

for track in album.tracks:
    print(f"{track.codec:<5.5} {track.title:<20.20} {track.artist:<20.20} "
          f"{track.probe_score:>4} "
          f"{track.duration_secs:>8.2f} {track.size:>12} {track.date:>6} "
          f"{track.sample_rate:>6} {track.channels:>2} "
          f"{track.fullpath}")

print ()
print (f'list source {album.listsource} has {album.track_count} tracks')
print (f'total seconds {album.totaltime}, average song length {album.totaltime // album.track_count}')

