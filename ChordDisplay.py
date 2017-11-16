from ButtonHandling import *
from ChordHandling import Song, Chords
from daGUI import TextScreen, EventModule, BUTTONEVENT
import sys
import time
import pygame
import os
import sys
from GuitarParty import guitarparty

#sys.stderr = open("stderr.txt", 'a')
#sys.stdout = open("stdout.txt", 'w+')

# print os.curdir

usbpath = "/media/usb/"
current_path = str(usbpath)
# usbpath = "C:\Users\SteinarrHrafn\PycharmProjects\ChordDisplay\TestFolder"

files_to_ignore = ["System Volume Information"]

if __name__ == '__main__':


    def button_callback(button):
        print("Button: ", button)
        event = EventModule.Event(BUTTONEVENT, message=str(button))
        EventModule.post(event)
    buttons = ButtonHandler()
    buttons.bind(button_callback)


    # print sys.argv[1]s
    if len(sys.argv) > 1 and ".song" in sys.argv[1]:
        ts = TextScreen(resolution=pygame.FULLSCREEN, mode="single")
        lag = Song(sys.argv[1])
        ts.add_song(lag)
        ts.display(lag)
        ts.main()
    else:
        ts = TextScreen(resolution=pygame.FULLSCREEN, mode='filesystem')
        done = False
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
                things = ["--Browse Guitarparty--"]
                things_fullname = ["GuitarParty"]
            else:
                things = ["../"]
                things_fullname = [current_path[:current_path.rfind("/")]]
            for thing in in_current_folder:
                if thing in files_to_ignore:
                    continue
                if ".song" in thing:
                    things.append(thing.strip('.song'))
                    things_fullname.append(current_path + "/" + thing)
                elif not "." in thing:
                    things.append("/" + thing)
                    things_fullname.append(current_path + "/" + thing)
            if len(things) > 0:
                print(things, things_fullname)
                picked_i = ts.pick_thing(things)
                if not os.path.exists(usbpath):
                    continue
                if picked_i is None:
                    done = True
                    break
                else:
                    picked = things_fullname[picked_i]
                    if picked == "GuitarParty"
                        guitarparty(ts)
                    if ".song" in picked:
                        ts.display(Song(picked))
                        ts.main()
                    else:
                        current_path = picked
