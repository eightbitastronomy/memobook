import parse
import curses.ascii
import config


class Tag(list):

    def __init__(self,t=None):
        self._mrk = config.TAG_MARKER
        if t is None:
            list.__init__(self)
        else:
            if type(t)==Tag or type(t)==list:
                list.__init__(self,t)
                return
            if type(t)==str:
                list.__init__(self)
                self.append(t)
                return

    def __str__(self):
        output = ""
        for item in self:
            output += self._mrk + str(item) + " "
        return output


    
class Note():

    def __init__(self,n=None):
        if n and type(n) == Note:
            self.title = str(n.title)     # file name
            self.text = str(n.text)       # body of the note
            self.tags = Tag(n.tags)       # the list of tags, no markers attached
            self.ID = str(n.ID)           # ties this note to a database entry or file descriptor
        else:
            self.title = ""
            self.text = ""
            self.tags = Tag(n)
            self.ID = ""

    def __str__(self):
        output = ""
        if self.text is not None:
            output += str(self.text)
        #if self.tags is not None:
        output += " " + str(self.tags)
        return output

    def parse(self):
        for t in parse.parse(self.text):
            self.tags.append(t)
