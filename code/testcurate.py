#!/usr/bin/python3

import music_curator as mc

# create track list with
# mpc -h wohnen -f %file% playlist | tail -n +7  | head > songlist.txt

#album = mc.TrackList('songlist.txt', '/home/nicolas/MP3')
#album = mc.TrackList('songlist.txt', '/srv/music')
album = mc.TrackList('songlist.txt', '/home/nick/share/mp3-coll')

for track in album.tracks:
    print(f"{track.codec:<5.5} {track.title:<20.20} {track.artist:<20.20} "
          f"{track.probe_score:>4} "
          f"{track.duration_secs:>8.2f} {track.size:>12} {track.date:>6} "
          f"{track.sample_rate:>6} {track.channels:>2} "
          f"{track.fullpath}")

print ()
print (f'list source {album.listsource} has {album.track_count} tracks')
print (f'total seconds {album.totaltime}, average song length {album.totaltime // album.track_count}')

