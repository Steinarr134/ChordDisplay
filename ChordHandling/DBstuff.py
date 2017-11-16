import sqlite3
import os

db_full_path = "/media/usb/songs.db"


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
