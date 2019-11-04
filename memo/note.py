###############################################################################################
#  note.py: the container classes for the user's files/data
#
#  Author (pseudonomously): eightbitastronomy (eightbitastronomy@protonmail.com)
#  Copyrighted by eightbitastronomy, 2019.
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
import memo.config as config
import enum



class NoteMime(enum.Enum):
    TEXT = 0
    IMAGE = 1
    PDF = 2
    OTHER = 99


class Tag(list):

    def __init__(self,t=None):
        self._mrk = config.TAG_MARKER
        self.silent = []
        if t is None:
            list.__init__(self)
        else:
            if type(t)==Tag:
                list.__init__(self,t)
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
        output = ""
        for item in self:
            output += self._mrk + str(item) + " "
        return output


    
class Note():

    def __init__(self,n=None):
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
        output = ""
        if self.body is not None:
            output += str(self.body)
        #if self.tags is not None:
        output += " " + str(self.tags)
        return output

    def parse(self):
        for t in parse.parse(self.body):
            self.tags.append(t)
