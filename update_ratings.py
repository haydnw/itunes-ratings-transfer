from collections import defaultdict
import plistlib

# I copied files locally.
# NEW is what gets written.
# OLD is an old backup with lots of good ratings.
OLD = 'Library.xml'
CURRENT = 'iTunes Music Library.xml'
NEW = 'updated.xml'

# I match based on filenames. IDs are different, sigh.
# But I needed to compensate for a new iTunes folder structure.
OLD_PREFIX1 = 'file://localhost/Users/Haydn/Music/'
OLD_PREFIX2 = 'file://localhost/Users/haydn/Music/'
OLD_PREFIX3 = 'file:///Users/Haydn/Music/'
OLD_PREFIX4 = 'file:///Users/haydn/Music/'
CURRENT_PREFIX = 'file:///Users/Haydn/Music/'


def main():
    # Read in the old tracks and grab the ratings.
    old = plistlib.readPlist(OLD)
    old_tracks = old['Tracks']
    print "Found " + str(len(old_tracks)).ljust(5) + " old tracks."
    old_ratings = {}
    for track in old_tracks.values():
        if "Location" in track:
            filename = track['Location']
            filename = filename.replace(OLD_PREFIX1, '')
            filename = filename.replace(OLD_PREFIX2, '')
            filename = filename.replace(OLD_PREFIX3, '')
            filename = filename.replace(OLD_PREFIX4, '')
            filename = filename.replace('haydn', 'Haydn')
            #print filename
            rating = track.get('Rating')
            if rating is not None:
                #print rating
                old_ratings[filename] = rating
            else:
                old_ratings[filename] = 0
    print "Found " + str(len(old_ratings)).ljust(5) + " old ratings."
    #print "The old ratings are:\n" + str(old_ratings)

    # Same with the current ratings. If we've rated something, we want to
    # keep that rating.
    current = plistlib.readPlist(CURRENT)
    current_tracks = current['Tracks']
    print "Found " + str(len(current_tracks)).ljust(5) + " current tracks."
 
    # Create a dict {rating: tracks} for the new ratings I want to set.
    new_playlists = defaultdict(list)
    skipcount = 0
    for track in current_tracks.values():
        filename = track['Location'].replace(CURRENT_PREFIX, '')
        filename = filename.replace('haydn', 'Haydn')
        #print filename
        if filename in old_ratings:
            old_rating = old_ratings[filename]
            track_id = track['Track ID']
            if old_rating is not None:
                new_playlists[old_rating].append(track_id)
            else:
                new_playlists[0].append(track_id)
        else:
            skipcount = skipcount + 1
    print "Skipped " + str(skipcount).ljust(5) + " tracks."

    # Create a playlist per rating. You can set the playlist's items to
    # the correct rating in iTunes just fine.
    playlists = []
    #new_playlists = sorted(new_playlists.keys())
    #for rating, track_ids in new_playlists.items():
    for rating, track_ids in sorted(new_playlists.iteritems()):
        stars = rating / 20
        print "Rating: " + str(stars) + " stars - " + str(len(track_ids)).ljust(4) + " tracks"
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
