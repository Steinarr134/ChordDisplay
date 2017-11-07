import os
import sqlite3


def guess_key(text):
    return text[0][text[0].find("%") + 1]

# Chords = [["C"],
#           ["C#", "Db"],
#           ["D"],
#           ["D#", "Eb"],
#           ["E"],
#           ["F"],
#           ["F#","Gb"],
#           ["G"],
#           ["G#", "Ab"],
#           ["A"],
#           ["Bb", "A#"],
#           ["B", "H"]]

Chords = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "Bb", "B"]

def _chord_number(key):
    for i, chord in enumerate(Chords):
        if key == chord:
            # print "key: {} is number {}".format(key, i)
            return i


def _change(s, i, n):
    # print s, i, n
    return s[:i] + n + s[i+1:]


def chord_translate(line, from_key, to_key):
    if "%" not in line:
        return line
    # print "Translating {} from {} to {}".format(line, from_key, to_key)
    startkeynr = _chord_number(from_key)
    endkeynr = _chord_number(to_key)
    diff = endkeynr - startkeynr
    # print "start:{}  end:{}   diff:{}".format(startkeynr, endkeynr, diff)
    changeline = str(line)
    while "%" in line:
        where = line.find("%")
        # print "changing: {} at {}".format(line, where)

        for i, chord in enumerate(Chords):
            if chord in line[where: where+3]:
                # print "\t replacing {} with {}".format(chord, Chords[(i+diff) % 12])
                line = line[:where] + " " + Chords[(i+diff) % 12] + line[where + 1 + len(chord):]
                break

    # print "result={}".format(line)
    return line

db_full_path = "/media/pi/SONGDRIVE/songs.db"

def db_exists():
    return os.path.exists(db_full_path)

def create_new_db():
    if not db_exists():
        db = sqlite3.connect(db_full_path)
        cursor = db.cursor()
        cursor.execute("CREATE TABLE songs(songname TEXT PRIMARY KEY, default_key TEXT)")
        cursor.close()
        db.commit()
        db.close()

def get_default_key_from_db(songname):
    if not db_exists():
        create_new_db()
    db = sqlite3.connect(db_full_path)
    cursor = db.cursor()
    cursor.execute("SELECT default_key FROM songs WHERE songname==?", [songname])
    row = cursor.fetchone()
    cursor.close()
    db.close()

    print("get_default_key_from_db found: ", row)

    if row is None:
        return None
    return row[0]

def write_default_key_to_db(songname, default_key):
    print("write_default_key_to_db")
    defkey = get_default_key_from_db(songname)
    if defkey == default_key:
        print("\tdb key({}) matched({}), bailing".format(defkey, default_key))
        return

    db = sqlite3.connect(db_full_path)
    cursor = db.cursor()
    if defkey is None:
        cursor.execute("INSERT INTO songs(songname, default_key) VALUES (?,?)", [songname, default_key])
    else:
        cursor.execute("UPDATE songs SET default_key=? WHERE songname==?", [default_key, songname])
    cursor.close()
    db.commit()
    db.close()

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
    def __init__(self, filename):
        self.FileName = filename
        self.Parts = []
        self.Name = self.FileName.split('/')[-1].strip('.song')

        with open(self.FileName, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # print lines

        if lines[0][:4] == "key=":
            starting_key = lines[0][4:].strip() if lines[0][4:].strip() in Chords else None

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

        self.CurrentPart = 0

        self.Key = get_default_key_from_db(self.FileName)
        if self.Key is None:
            self.Key = starting_key
            write_default_key_to_db(self.FileName, starting_key)

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
            write_default_key_to_db(self.FileName, newkey)

    def change_key_by(self, c):
        p = Chords.index(self.Key)
        newkey = Chords[(p + c) % 12]
        self.set_key(newkey)



if __name__ == '__main__':
    skapa = Song("..\\TestFiles\\Skapa.txt")
    print(skapa.Parts[0].get())