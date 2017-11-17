
def guess_key(text):
    return text[0][text[0].find("%") + 1]

AllChords = [["C"],
             ["C#", "Db"],
             ["D"],
             ["D#", "Eb"],
             ["E"],
             ["F"],
             ["F#","Gb"],
             ["G"],
             ["G#", "Ab"],
             ["A"],
             ["Bb", "A#"],
             ["B", "H"]]


def get_chord_i_and_l(s):
    # print("looking for ", s)
    l = 1
    if len(s) > 1 and (s[1] == "#" or s[1] == "b"):
        l = 2
    for i, versions in enumerate(AllChords):
        for version in versions:
            if s[:l] == version:
                return (i, l)
    raise TypeError("I don't think {} is a valid chord".format(s))


Chords = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "Bb", "B"]


def clean_chord(chord):
    if chord[:2] in Chords:
        return chord[:2]
    elif chord[0] in Chords:
        return chord[0]
    else:
        return None


def chord_translate(line, from_key, to_key):
    if "%" not in line:
        return line
    # print "Translating {} from {} to {}".format(line, from_key, to_key)
    startkeynr = get_chord_i_and_l(from_key)[0]
    endkeynr = get_chord_i_and_l(to_key)[0]
    diff = endkeynr - startkeynr
    # print "start:{}  end:{}   diff:{}".format(startkeynr, endkeynr, diff)
    while "%" in line:
        where = line.find("%")
        # print "changing: {} at {}".format(line, where)
        i, l = get_chord_i_and_l(line[where + 1: where + 4])
        line = line[:where] + " " + Chords[(i+diff) % 12] + line[where + 1 + l:]

    # print "result={}".format(line)
    return line
