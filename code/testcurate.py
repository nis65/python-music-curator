#!/usr/bin/python3

import music_curator as mc
import argparse


parser = argparse.ArgumentParser(
    prog=__file__,
    description="Do some tests with the music_curator",
    epilog="Have fun!",
)
parser.add_argument("-p", "--playlist")
parser.add_argument("-m", "--musicbase")
parser.add_argument("-s", "--size")
parser.add_argument("-d", "--duration")

args = parser.parse_args()

if args.playlist:
    inputplaylist = args.playlist
else:
    inputplaylist = "songlist.txt"

if args.musicbase:
    musicbase = args.musicbase
else:
    musicbase = "/home/nick/share/mp3-coll"

if args.size:
    maxsize = int(args.size)
else:
    maxsize = 500 * 1000 * 1000 * 1000

if args.duration:
    maxduration = float(args.duration)
else:
    maxduration = float(60 * 60 * 24 * 365 * 10)

print(f'analyzing playlist "{inputplaylist}" and searching music in "{musicbase}"')

# create track from mpd list with
# mpc -h wohnen -f %file% playlist | tail -n +7  | head > songlist.txt

# with old __init__
# album = mc.TrackList(inputplaylist, musicbase, max_seconds=maxduration, max_size=maxsize)

album = mc.TrackList(max_seconds=maxduration, max_size=maxsize)
album.detect_from_playlistfile(inputplaylist, musicbase)

print("-----")
print(album)
print("-----")
print(album.pp(with_tracks=False))
print("=====")

shortalbum = mc.TrackList()
print(shortalbum)
print(shortalbum.pp())

shortalbum.tracks = [track for track in album.tracks if track.duration_secs < 60 * 3]
shortalbum.musicbase = album.musicbase
print(shortalbum)
print(shortalbum.pp())

print("=====")

bigalbum = album
bigalbum.tracks = [track for track in album.tracks if track.size > 40 * 1000 * 1000]
print(bigalbum.pp())
