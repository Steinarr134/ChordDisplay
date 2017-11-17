from ButtonHandling import *
from ChordHandling import FileSong, Chords
from daGUI import TextScreen, EventModule, BUTTONEVENT
import pygame
import os
import sys
from GuitarParty import guitarparty, guitarparty_available

# sys.stderr = open("stderr.txt", 'a')
# sys.stdout = open("stdout.txt", 'w+')

# print os.curdir

# usbpath = "/media/usb/"
usbpath = "C:\\Users\SteinarrHrafn\Documents\GitHub\ChordDisplay\TestFolder"
current_path = str(usbpath)

files_to_ignore = ["System Volume Information"]

if __name__ == '__main__':
    offer_guitarparty = guitarparty_available()


    def button_callback(button):
        print("Button: ", button)
        event = EventModule.Event(BUTTONEVENT, message=str(button))
        EventModule.post(event)
    buttons = ButtonHandler()
    buttons.bind(button_callback)

    # print sys.argv[1]s
    if len(sys.argv) > 1 and ".song" in sys.argv[1]:
        ts = TextScreen(resolution=pygame.FULLSCREEN, mode="single")
        lag = FileSong(sys.argv[1])
        ts.add_song(lag)
        ts.display(lag)
        ts.main()
    else:
        ts = TextScreen(resolution=pygame.FULLSCREEN, mode='filesystem')
        done = False
        selecteds = {usbpath: 0}
        while not done:
            if not os.path.exists(usbpath):
                current_path = str(usbpath)
                done = ts.wait_for(lambda: os.path.exists(usbpath), "Insert usb to start")
                if done:
                    break
            in_current_folder = os.listdir(current_path)
            # print(in_current_folder)
            ts.clear_songs()
            if current_path == usbpath:
                if offer_guitarparty:
                    things = ["--Browse Guitarparty--"]
                    things_fullname = ["GuitarParty"]
                else:
                    things = []
                    things_fullname = []
            else:
                things = ["../"]
                things_fullname = [current_path[:current_path.rfind("/")]]
            for thing in in_current_folder:
                if thing in files_to_ignore:
                    continue
                if ".song" in thing:
                    things.append(thing.strip('.song'))
                    things_fullname.append(current_path + "/" + thing)
                elif "." not in thing:
                    things.append("/" + thing)
                    things_fullname.append(current_path + "/" + thing)
            if len(things) > 0:
                print(things, things_fullname)
                if current_path not in selecteds:
                    selecteds[current_path] = 1
                picked_i = ts.pick_thing(things, selected=selecteds[current_path])
                if not os.path.exists(usbpath):
                    continue
                if picked_i is None:
                    done = True
                    break
                else:
                    picked = things_fullname[picked_i]
                    if picked == "GuitarParty":
                        guitarparty(ts)
                    elif ".song" in picked:
                        ts.display(FileSong(picked))
                        ts.main()
                    else:
                        selecteds[current_path] = picked_i
                        current_path = picked

