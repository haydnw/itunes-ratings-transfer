from collections import defaultdict
import plistlib
 
# I copied files locally.
# NEW is what gets written.
# CURRENT is the current "iTunes Library.xml" file (or rather, my copy).
# OLD is an old backup with lots of good ratings.
OLD = 'itunes.xml'
CURRENT = 'itunes_2012.xml'
NEW = 'updated.xml'
 
# I match based on filenames. IDs are different, sigh.
# But I needed to compensate for a new iTunes folder structure.
OLD_PREFIX = 'file://localhost/Users/reinout/Music/iTunes/iTunes%20Music/'
CURRENT_PREFIX = 'file://localhost/Users/reinout/Music/iTunes/iTunes%20Media/Music/'
 
 
def main():
    # Read in the old tracks and grab the ratings.
    old = plistlib.readPlist(OLD)
    old_tracks = old['Tracks']
    print "Found {} old tracks".format(len(old_tracks))
    old_ratings = {}
    for track in old_tracks.values():
        filename = track['Location'].replace(OLD_PREFIX, '')
        rating = track.get('Rating')
        if rating is None:
            continue
        old_ratings[filename] = rating
    print "Found {} old ratings".format(len(old_ratings))
 
    # Same with the current ratings. If we've rated something, we want to
    # keep that rating.
    current = plistlib.readPlist(CURRENT)
    current_tracks = current['Tracks']
    print "Found {} current tracks".format(len(current_tracks))
    current_ratings = {}
    for track in current_tracks.values():
        filename = track['Location'].replace(CURRENT_PREFIX, '')
        rating = track.get('Rating')
        if rating is None:
            continue
        current_ratings[filename] = rating
    print "Found {} current ratings".format(len(current_ratings))
 
    # Figure out which old ratings we want to move over.
    new_ratings = {}
    for filename in old_ratings:
        if filename not in current_ratings:
            new_ratings[filename]= old_ratings[filename]
    print "This means {} new ratings".format(len(new_ratings))
 
    # Create a dict {rating: tracks} for the new ratings I want to set.
    new_playlists = defaultdict(list)
    for track in current_tracks.values():
        filename = track['Location'].replace(CURRENT_PREFIX, '')
        new_rating = new_ratings.get(filename)
        if new_rating is None:
            continue
        track_id = track['Track ID']
        new_playlists[new_rating].append(track_id)
 
    # Create a playlist per rating. You can set the playlist's items to
    # the correct rating in iTunes just fine.
    playlists = []
    for rating, track_ids in new_playlists.items():
        print rating, len(track_ids)
        new_playlist = {}
        new_playlist['Name'] = str(rating) + ' points'
        new_playlist['Visible'] = True
        new_playlist['Playlist ID'] = 8000 + rating
        new_playlist['All Items'] = True
        new_playlist['Playlist Items'] = [{'Track ID': track_id}
                                          for track_id in track_ids]
        playlists.append(new_playlist)
    # Zap the existing ones, otherwise you end up with double items.
    current['Playlists'] = playlists
    plistlib.writePlist(current, NEW)
 
 
if __name__ == '__main__':
    main()
