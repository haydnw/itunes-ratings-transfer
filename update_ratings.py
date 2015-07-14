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
    print("Calculating...")

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
            rating = track.get('Rating')
            if rating is not None:
                # Rating is one to five
                old_ratings[filename] = rating
            else:
                # Rating is zero
                old_ratings[filename] = 0
    print "Found " + str(len(old_ratings)).ljust(5) + " old ratings."

    # Get the list of current tracks (we need to include their current
    # iTunes ID number in the new playlists).
    current = plistlib.readPlist(CURRENT)
    current_tracks = current['Tracks']
    print "Found " + str(len(current_tracks)).ljust(5) + " current tracks."
 
    # Create a dict {rating: tracks} for the new ratings I want to set.
    new_playlists = defaultdict(list)
    skipcount = 0
    for track in current_tracks.values():
        filename = track['Location'].replace(CURRENT_PREFIX, '')
        if filename in old_ratings:
            old_rating = old_ratings[filename]
            track_id = track['Track ID']
            if old_rating is not None:
                # Rating is one to five
                new_playlists[old_rating].append(track_id)
            else:
                # Rating is zero
                new_playlists[0].append(track_id)
        else:
            skipcount = skipcount + 1
    print "Skipped " + str(skipcount).ljust(3) + " tracks."

    # Actually create a playlist per rating from the dict.
    playlists = []
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
    print("Writing new playlist(s) to " + NEW + "...")
    current['Playlists'] = playlists
    plistlib.writePlist(current, NEW)

    print("Finished!")

if __name__ == '__main__':
    main()
