import requests
from ChordHandling.ChordHandlingCode import Song, SongPart
from .TranslateFormat import translate_to_parts
API_KEY = "817ffd6d92ebd4b8579c0da1e1eff52ecb7ceb80"
headers = {'Guitarparty-Api-Key': API_KEY}
api = "http://api.guitarparty.com"


class GuitarPartySong(Song):
    def __init__(self, d):
        Song.__init__(self)
        self._d = d
        self.title = d['song']['title']
        self.Title = self.title
        self.Key = d['key']
        self.FileName = d['uri']
        self.uri = d['uri']
        parts = translate_to_parts(d['song']['body'])[1:]

        self.Parts = [SongPart([line + '\n' for line in part.splitlines()], self.Key) for part in parts]
        part0 = self.Parts[0]
        # print(part0.Lines)


class SongBook(object):
    def __init__(self, d):
        self.is_public = d['is_public']
        self.description = d['description']
        self.title = d['title']
        self.uri = d['uri']
        self.Songs = []

    def load_songs(self):
        if not self.Songs:
            r = requests.get(api + self.uri + "songs/", headers=headers)
            for song_d in r.json()['objects']:
                self.Songs.append(GuitarPartySong(song_d))

    def get_songs(self):
        self.load_songs()
        return self.Songs


def get_songbooks():
    r = requests.get(api+"/v2/songbooks/", headers=headers)
    j = r.json()
    ret = []
    for book_d in j['objects']:
        ret.append(SongBook(book_d))
    return ret


if __name__ == '__main__':
    songbooks = get_songbooks()
    sb = songbooks[0]
    sb.get_songs()