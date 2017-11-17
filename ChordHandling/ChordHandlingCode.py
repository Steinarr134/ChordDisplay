from .DBstuff import *
from .ChordFunctions import *


def _change(s, i, n):
    # print s, i, n
    return s[:i] + n + s[i+1:]


class SongPart(object):
    def __init__(self, lines, key=None):
        self.Lines = lines
        # print lines
        self.Key = key if key is not None else guess_key(lines[0])

        # Make sure keys are upper case
        for line in self.Lines:
            # print line
            for i, letter in enumerate(line):
                if letter == "%":
                    line = _change(line, i+1, line[i+1].upper())

    def get(self):
        return self.get_in_key(self.Key)

    def get_in_key(self, key):
        ret = []
        for line in self.Lines:
            ret.append(chord_translate(line, self.Key, key))
        return "".join(ret)


class Song(object):
    def __init__(self):
        self.Parts = []
        self.Name = None
        self.FileName = None
        self.CurrentPart = 0
        self.Key = Chords[0]

    def current(self):
        return self.Parts[self.CurrentPart].get_in_key(self.Key)

    def next(self):
        # print self.CurrentPart
        self.CurrentPart = min(len(self.Parts)-1, self.CurrentPart + 1)
        # print self.CurrentPart
        return self.Parts[self.CurrentPart].get_in_key(self.Key)

    def previous(self):
        self.CurrentPart = max(0, self.CurrentPart - 1)
        return self.Parts[self.CurrentPart].get_in_key(self.Key)

    def set_key(self, newkey):
        if newkey in Chords:
            self.Key = newkey
            if self.FileName is not None:
                write_default_key_to_db(self.FileName, newkey)

    def change_key_by(self, c):
        p = Chords.index(self.Key)
        newkey = Chords[(p + c) % 12]
        self.set_key(newkey)


class FileSong(Song):
    def __init__(self, filename):
        Song.__init__(self)
        self.FileName = filename
        self.Name = self.FileName.split('/')[-1].split('.')[0]
        self.load_parts()

    def load_parts(self):
        with open(self.FileName, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # print lines

        if lines[0][:4] == "key=":
            if lines[0][4:].strip()[:2] in Chords:
                starting_key = lines[0][4:].strip()[:2]
            elif lines[0][4:].strip()[0] in Chords:
                starting_key = lines[0][4:].strip()[0]
            else:
                starting_key = None
        else:
            starting_key = None

        temp = []
        for line in lines[1:]:
            # print line
            if "===" in line:
                # print "found ======"
                self.Parts.append(SongPart(temp, starting_key))
                temp = []
            else:
                temp.append(line)
        self.Parts.append(SongPart(temp, starting_key))

        self.Key = get_default_key_from_db(self.FileName)
        if self.Key is None:
            self.Key = starting_key
            write_default_key_to_db(self.FileName, starting_key)


if __name__ == '__main__':
    skapa = FileSong("..\\TestFiles\\Skapa.txt")
    print(skapa.Parts[0].get())