from .SongBooks import get_songbooks
import socket


def guitarparty_available():
    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname("guitarparty.com")
        # connect to the host -- tells us if the host is actually
        # reachable
        s = socket.create_connection((host, 80), 2)
        return True
    except socket.error as e:
        print(e)
    return False


def guitarparty(ts):
    done = False
    picked_s_i = 1
    picked_sb_i = 1
    # Search through songbooks
    songbooks = get_songbooks()
    songbooknames = ["<--back"] + [sb.title for sb in songbooks]
    while not done:
        # Pick one Songbook
        picked_sb_i = ts.pick_thing(songbooknames, selected=picked_sb_i)
        if picked_sb_i is None:
            break
        elif picked_sb_i == 0:
            break
        songbook = songbooks[picked_sb_i - 1]
        songs = songbook.get_songs()
        songnames = ["<--back"] + [s.title for s in songs]
        while True:
            # load songs from songbook
            picked_s_i = ts.pick_thing(songnames, selected=picked_s_i)
            if picked_s_i is None:
                done = True
                break
            elif picked_s_i == 0:
                break
            ts.display(songs[picked_s_i - 1])
            ts.main()


