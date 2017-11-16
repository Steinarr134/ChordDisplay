import os


def guitarparty(ts):
    # TODO: Search through songbooks
    songbooks = []

    picked_i = ts.pick_thing(songbooks)

    # TODO: load songs from songbook
    songs = []
    picked_i = ts.pick_thing(songs)

    # TODO: display that song

