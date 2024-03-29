###############################################################################################
#  note.py: the container classes for the user's files/data
#
#  Author: Miguel Abele
#  Copyrighted by Miguel Abele, 2020.
#
#  License information:
#
#  This file is a part of Memobook Note Suite.
#
#  Memobook Note Suite is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  Memobook Note Suite is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
###############################################################################################


'''Note and Tag classes for Memobook'''


import memo.parse as parse
import curses.ascii
import enum
from memo.config import TAG_MARKER
from memo.debug import dprint



class NoteMime(enum.Enum):

    '''Enumeration of mime types for note contents'''

    
    TEXT = 0
    IMAGE = 1
    PDF = 2
    OTHER = 99



class Tag(list):

    '''List-based class for dynamic storage of bookmarks'''

    
    def __init__(self, t=None):
        dprint(3, "\nTag::__init__")
        self._mrk = TAG_MARKER
        self.silent = []
        if t is None:
            list.__init__(self)
        else:
            if type(t)==Tag:
                list.__init__(self, t)
                self.silent = list(t.silent)
                return
            if type(t)==list:
                list.__init__(self,t)
                return
            if type(t)==str:
                list.__init__(self)
                self.append(t)
                return
            

    def __str__(self):
        dprint(3, "\nTag::__str__")
        output = ""
        for item in self:
            output += self._mrk + str(item) + " "
        return output



class Note():

    '''Note class: holds file contents, path, tags and silent tags, title, and mime-type'''

    
    def __init__(self, n=None):
        dprint(3, "\nNote::__init__")
        #initialization depends on what, if anything, is passed in as an argument'''
        if n and type(n) == Note:
            self.title = str(n.title)     # file name
            self.body = str(n.body)       # body of the note
            self.tags = Tag(n.tags)       # the list of tags, no markers attached
            self.ID = str(n.ID)           # ties this note to a database entry or file descriptor
            self.mime = n.mime            # type of file: text,pdf,image,etc
        else:
            self.title = ""
            self.body = None
            self.tags = Tag(n)
            self.ID = ""
            self.mime = NoteMime.OTHER

            
    def __str__(self):
        dprint(3, "\nNote::__str__")
        output = ""
        if self.body is not None:
            output += str(self.body)
        output += " " + str(self.tags)
        return output

    
    def parse(self):
        '''Scan note body for bookmarks via parse function'''
        dprint(3, "\nNote::parse")
        for t in parse.parse(self.body):
            self.tags.append(t)
