#!/usr/bin/env python


import pygame
import threading
import time

pygame.init()
time.sleep(0.1) 
EventModule = pygame.fastevent
EventModule.init()
DISPEVENT = pygame.USEREVENT + 1
BUTTONEVENT = pygame.USEREVENT + 2


class TextRectException:
    def __init__(self, message=None):
            self.message = message

    def __str__(self):
        return self.message


def multiLineSurface(string, font, rect, fontColour, BGColour, justification=0):
    """Returns a surface containing the passed text string, reformatted
    to fit within the given rect, word-wrapping as necessary. The text
    will be anti-aliased.

    Parameters
    ----------
    string - the text you wish to render. \n begins a new line.
    font - a Font object
    rect - a rect style giving the size of the surface requested.
    fontColour - a three-byte tuple of the rgb value of the
             text color. ex (0, 0, 0) = BLACK
    BGColour - a three-byte tuple of the rgb value of the surface.
    justification - 0 (default) left-justified
                1 horizontally centered
                2 right-justified

    Returns
    -------
    Success - a surface object with the text rendered onto it.
    Failure - raises a TextRectException if the text won't fit onto the surface.
    """

    finalLines = []
    requestedLines = string.splitlines()
    # Create a series of lines that will fit on the provided
    # rectangle.
    for requestedLine in requestedLines:
        if font.size(requestedLine)[0] > rect.width:
            words = requestedLine.split(' ')
            # if any of our words are too long to fit, return.
            for word in words:
                if font.size(word)[0] >= rect.width:
                    raise TextRectException("The word " + word + " is too long to fit in the rect passed.")
            # Start a new line
            accumulatedLine = ""
            for word in words:
                testLine = accumulatedLine + word + " "
                # Build the line while the words fit.
                if font.size(testLine)[0] < rect.width:
                    accumulatedLine = testLine
                else:
                    finalLines.append(accumulatedLine)
                    accumulatedLine = word + " "
            finalLines.append(accumulatedLine)
        else:
            finalLines.append(requestedLine)

    # Let's try to write the text out on the surface.
    surface = pygame.Surface(rect.size)
    surface.fill(BGColour)
    accumulatedHeight = 0
    for line in finalLines:
        if accumulatedHeight + font.size(line)[1] >= rect.height:
            raise TextRectException("Once word-wrapped, the text string was too tall to fit in the rect.")
        if line != "":
            tempSurface = font.render(line, 1, fontColour)
        if justification == 0:
            surface.blit(tempSurface, (0, accumulatedHeight))
        elif justification == 1:
            surface.blit(tempSurface, ((rect.width - tempSurface.get_width()) / 2, accumulatedHeight))
        elif justification == 2:
            surface.blit(tempSurface, (rect.width - tempSurface.get_width(), accumulatedHeight))
        else:
            raise TextRectException("Invalid justification argument: " + str(justification))
        accumulatedHeight += font.size(line)[1]
    return surface

def my_rect_placer(text, rect, fg, bg, fonttype=None, justification=0, underscore_line_nrs=()):
    if type(text) is str:
        lines = text.split('\n')
    else:
        lines = text
    lines = [line if line != "" else " " for line in lines]
    nof_lines = len(lines)
    if nof_lines == 0:
        lines.append("(nothing)")
        nof_lines = 1
    # print rect.size
    fontsize = min(int((0.9*rect.size[1]/nof_lines)), 100)
    #print("{} lines and {} height, putting fontsize to {}".format(nof_lines, rect.size[1], fontsize))
    font = pygame.font.SysFont(fonttype, fontsize)
    longest_line_width = 0
    for line in lines:
        l = font.size(line)[0]
        # print l
        if l > longest_line_width:
            longest_line_width = l
    #print(lines)
    if longest_line_width > rect.size[0]:
        fontsize = int((rect.size[0]/float(longest_line_width))*fontsize)
        #print("longest line is {} side and width is {}, changing fontsize to {}".format(longest_line_width, rect.size[0], fontsize))
    font = pygame.font.SysFont(fonttype, fontsize)
    fontheight = sum([font.size(line)[1] for line in lines])
    fontwidth = font.size(max(lines, key=lambda l: font.size(l)[0]))[0]
    surface = pygame.Surface(rect.size)
    surface.fill(bg)

    leftoffset = (rect.size[0] - fontwidth)/2
    accumulatedHeight = (rect.size[1] - fontheight)/2
    for i, line in enumerate(lines):
        font.set_underline(i in underscore_line_nrs)
        if accumulatedHeight + font.size(line)[1] >= rect.height:
            raise Exception("Once word-wrapped, the text string ({}) was too tall to fit in the rect({}).".format(line, (rect.height, rect.width)))
        if line != "":
            tempSurface = font.render(line.strip('\r'), 1, fg)
        if justification == 0:
            surface.blit(tempSurface, (leftoffset, accumulatedHeight))
        elif justification == 1:
            surface.blit(tempSurface, ((rect.width - tempSurface.get_width()) / 2, accumulatedHeight))
        elif justification == 2:
            surface.blit(tempSurface, (rect.width - tempSurface.get_width(), accumulatedHeight))
        else:
            raise TextRectException("Invalid justification argument: " + str(justification))
        accumulatedHeight += font.size(line)[1]
    return surface


class TextScreen(object):
    def __init__(self, resolution=(400, 600), mode='pick'):
        # threading.Thread.__init__(self)
        self.Mode = mode
        if resolution == pygame.FULLSCREEN:
            self.Screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.Resolution = self.Screen.get_size()

            pygame.mouse.set_visible(False)
            #print(self.Resolution)
        else:
            self.Resolution = resolution
            self.Screen = pygame.display.set_mode(resolution)
        self.bg = 0, 0, 0
        self.fg = 255, 255, 255
        self.Screen.fill(self.bg)
        self.BoundaryWidth = 5
        self.Rect = pygame.Rect(self.BoundaryWidth, self.BoundaryWidth,
                                self.Resolution[0] - 2*self.BoundaryWidth,
                                self.Resolution[1] - 2*self.BoundaryWidth)

        self.Font = pygame.font.Font(None, 80)
        # pygame.display.flip()
        self.CurrentSong = None
        self.Songs = []
        self.Song_i = -1
        self.SongOrder = []
        # self.start()

    def clear_songs(self):
        self.CurrentSong = None
        self.Songs = []
        self.Song_i = -1
        self.SongOrder = []

    def add_song(self, song):
        #print "adding {}".format(song.Name)
        self.Songs.append(song)
        self.SongOrder.append(None)

    def disp_songlist(self, highlight_nr):
        pass

    def wait_for(self, check_fun, text):
        waitdoneevent = pygame.USEREVENT + 2

        stopthread = threading.Event()

        def checkingfun():
            while not check_fun():
                time.sleep(0.5)
                if stopthread.isSet():
                    return
            event = EventModule.Event(waitdoneevent)
            EventModule.post(event)

        t = threading.Thread(target=checkingfun)
        t.start()

        render = my_rect_placer(text,
                                self.Rect, self.fg, self.bg)
        self.Screen.blit(render, (self.BoundaryWidth, self.BoundaryWidth))
        pygame.display.flip()
        done = False
        ret = False
        while not done:
            for event in EventModule.get():
                if event.type == waitdoneevent:
                    done = True
                elif  (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    done = True
                    ret = True
        stopthread.set()
        t.join()
        return ret

    def pick_thing(self, things, selected=0):
        done = False
        selected = int(selected)
        n = len(things)
        goingdown = True
        maxlines = 10
        start_i = selected
        stop_i = min(maxlines, n)
        while not done:
            songnamelist = []
            underscored = [selected - start_i]
            for i in range(start_i, stop_i):
                songnamelist.append(" "*5 + things[i]+ " "*5)

            self.Screen.fill(self.bg)
            render = my_rect_placer(songnamelist, self.Rect, self.fg, self.bg, underscore_line_nrs=underscored)
            self.Screen.blit(render, (self.BoundaryWidth, self.BoundaryWidth))
            pygame.display.flip()

            for event in EventModule.get():

                if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    return None
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT) \
                    or (event.type == BUTTONEVENT and event.message == "3"):
                    selected = max(0, selected - 1)
                    if selected < start_i:
                        stop_i -= 1
                        start_i -= 1
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT) \
                    or (event.type == BUTTONEVENT and event.message == "4"):
                    selected = min(n - 1, selected + 1)
                    if selected > stop_i - 1:
                        stop_i += 1
                        start_i += 1
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_UP) \
                    or (event.type == BUTTONEVENT and event.message == "1"):
                    return selected

    def pick_song(self):
        done = False
        selected = 0
        n = len(self.Songs)
        while not done:
            songnamelist = []
            underscored = [selected]
            for i in range(len(self.Songs)):
                songnamelist.append(" "*5 + self.Songs[i].Name+ " "*5)

            self.Screen.fill(self.bg)
            render = my_rect_placer(songnamelist, self.Rect, self.fg, self.bg, underscore_line_nrs=underscored)
            self.Screen.blit(render, (self.BoundaryWidth, self.BoundaryWidth))
            pygame.display.flip()

            for event in EventModule.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return True
                    elif event.key == pygame.K_LEFT:
                        selected = next(((x + selected) % n for x in reversed(range(n)) if
                                        self.SongOrder[(x + selected) % n] is None),
                                        max(0, selected - 1))
                    elif event.key == pygame.K_RIGHT:
                        selected = next(((x + selected + 1) % n for x in range(n) if
                                         self.SongOrder[(x + selected + 1) % n] is None),
                                        min(n, selected + 1))
                    elif event.key == pygame.K_UP:
                        self.display(self.Songs[selected])
                        return False

    def order_songs(self):
        done = False
        selected = 0
        next_select_nr = 1
        n = len(self.Songs)
        while not done:
            songnamelist = []
            underscored = [selected]
            for i in range(len(self.Songs)):
                line = ""
                if self.SongOrder[i] is None:
                    line += "    "
                else:
                    toappend = str(self.SongOrder[i]) + "    "
                    line += toappend[:4]
                line += self.Songs[i].Name
                songnamelist.append(line)

            self.Screen.fill(self.bg)
            render = my_rect_placer(songnamelist, self.Rect, self.fg, self.bg, underscore_line_nrs=underscored)
            self.Screen.blit(render, (self.BoundaryWidth, self.BoundaryWidth))
            pygame.display.flip()

            for event in EventModule.get():
                if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    done = True
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT) \
                    or (event.type == BUTTONEVENT and event.message == "4"):
                    selected = next(((x + selected) % n for x in reversed(range(n)) if
                                    self.SongOrder[(x + selected) % n] is None),
                                    max(0, selected - 1))
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT) \
                    or (event.type == BUTTONEVENT and event.message == "3"):
                    selected = next(((x + selected + 1) % n for x in range(n) if
                                     self.SongOrder[(x + selected + 1) % n] is None),
                                    min(n, selected + 1))
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_UP) \
                    or (event.type == BUTTONEVENT and event.message == "1"):
                    # print next_select_nr, n
                    if next_select_nr > n:
                        done = True
                        # print "done=True"
                        break
                    if self.SongOrder[selected] is None:
                        self.SongOrder[selected] = next_select_nr
                        next_select_nr += 1
                        selected = next(((x + selected + 1) % n for x in range(n) if
                                        self.SongOrder[(x + selected + 1) % n] is None),
                                        min(n, selected + 1))
                        if next_select_nr > n:
                            selected = -1

        ordered_songs = []
        for i in range(n):
            ordered_songs.append(self.Songs[self.SongOrder[i] - 1])
        self.Songs = ordered_songs
        self.next_song()

    def next_song(self):
        self.Song_i = min(len(self.Songs) - 1, self.Song_i + 1)
        self.display(self.Songs[self.Song_i])

    def previous_song(self):
        self.Song_i = max(0, self.Song_i - 1)
        self.display(self.Songs[self.Song_i])

    def main(self):
            
        if self.Mode == "pick":
            if len(self.Songs) == 0:
                self.wait_for(lambda: False, "No files ending in .song found :(")
            done = self.pick_song()
            if done:
                return True
        elif self.Mode == 'order':
            if len(self.Songs) == 0:
                self.wait_for(lambda: False, "No files ending in .song found :(")
            self.order_songs()
        done = False
        while not done:
            #use event.wait to keep from polling 100% cpu
            for event in EventModule.get():

                if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    return True
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT) \
                        or (event.type == BUTTONEVENT and event.message == "3"):
                    if self.CurrentSong is not None:
                        self.display(self.CurrentSong.previous())
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT) \
                        or (event.type == BUTTONEVENT and event.message == "4"):
                    # print "Right Pressed"
                    if self.CurrentSong is not None:
                        self.display(self.CurrentSong.next())
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_UP) \
                        or (event.type == BUTTONEVENT and event.message == "1"):
                    if self.Mode == 'order':
                        self.next_song()
                    elif self.Mode == 'pick':
                        done = True
                    else:
                        done = True
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN):
                    if self.Mode == 'order':
                        self.previous_song()
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_u) \
                        or (event.type == BUTTONEVENT and event.message == "2"):
                    if self.CurrentSong is not None:
                        self.CurrentSong.change_key_by(1)
                        self.display(self.CurrentSong.current())
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_d) \
                        or (event.type == BUTTONEVENT and event.message == "0"):
                    if self.CurrentSong is not None:
                        self.CurrentSong.change_key_by(-1)
                        self.display(self.CurrentSong.current())
                elif event.type == DISPEVENT:
                    # print "DISPEVENT REceived"
                    self.Screen.fill(self.bg)
                    render = my_rect_placer(event.message, self.Rect, self.fg, self.bg, fonttype="monospace")
                    self.Screen.blit(render, (self.BoundaryWidth, self.BoundaryWidth))
                    pygame.display.flip()
        return False
        # print "TextScreen Done!!!!!!!!!!!!!"

    def put_search_button_on_screen(self):
        return
        # surface = pygame.Surface(self.SearchButtonSize)
        # surface.fill((255, 0, 0))
        # self.Screen.blit(surface, (0, 0))

    def display(self, what):
        if type(what) is str:
            dispevent = EventModule.Event(DISPEVENT, message=what)
            EventModule.post(dispevent)
            # print "Stuff posted to Eventmodule"
        else:
            self.CurrentSong = what
            self.display(what.current())

if __name__ == '__main__':
    ts = TextScreen()

    def foo():
        while True:
            text = raw_input("What to write?  ")
            ts.display(text)

    t = threading.Thread(target=foo)
    t.setDaemon(True)
    t.start()

    ts.main()
