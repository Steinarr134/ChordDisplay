from ChordHandling.ChordFunctions import clean_chord


def translate_to_parts(text):
    text = text.replace('\t', "    ")
    if '\r' in text:
        parts = text.split('\r\n\r\n')
    else:
        parts = text.split('\n\n')

    transparts = [""]

    part_i = 1
    keyfound = False
    for part in parts:
        if "[" not in part:
            continue
        transparts.append("\n")
        for line in part.splitlines():
            line = line.strip()
            chordline = ""
            while '[' in line:
                # print(line)
                i = line.find('[')
                j = line.find(']')
                if not keyfound:
                    keyfound = True
                    transparts[0] = "key=" + clean_chord(line[i+1:j]) + "\n"*2
                chordline += " "*(i - len(chordline)) + "%" + line[i+1:j]
                line = line[:i] + line[j+1:]
            transparts[part_i] += chordline + "\n" + line + "\n"*2
            # print(chordline)
            # print(line)
        # transparts[part_i] += "=================\n"
        part_i += 1
        # print("=========")
    return transparts

def translate_and_write(text, filename):
    transparts = translate_to_parts(text)
    with open("Jolene.song", 'w+') as f:
        for part in transparts:
            f.write(part)
            f.write("========\n")

