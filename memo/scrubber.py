###############################################################################################
#  scrubber.py: XML utilities for whitespace removal and tree parsing
#
#  Author (pseudonomously): eightbitastronomy (eightbitastronomy@protonmail.com)
#  Copyrighted by eightbitastronomy, 2020.
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



'''XML scrubbing utilities / classes'''


import enum
from memo.debug import dprint




class Stack:

    '''A bare-bones stack implementation'''

    ### This stack is, at the moment, over-kill. ScrubberXML really only needs a counter.
    ### However, in the future I may expand ScrubberXML into something that really does need a stack.

    
    def __init__(self, depth):
        dprint(3, "\nStack::__init__")
        self.__depth = depth
        self.__list = []
        self.__top = 0

        
    def push(self, item):
        '''Push item onto stack'''
        dprint(3, "\nStack::push")
        if self.__top == self.__depth:
            raise Exception("Stack depth (" + str(self.__depth) + ") exceeded")
        self.__top += 1
        self.__list.append(item)

        
    def pop(self):
        '''Pop item from stack'''
        dprint(3, "\nStack::pop")
        if self.__top == 0:
            return None
        self.__top -= 1
        return self.__list.pop(self.__top)

    
    def __str__(self):
        dprint(3, "\nStack::__str__")
        build_str = ""
        for i in range(0, self.__top):
            k = i
            while k>0:
                build_str += ">"
                k -= 1
            build_str += str(self.__list[self.__top-i-1]) + "\n"
        return build_str



    
class xml(enum.Enum):
    
    '''Enumeration class for states during an XML parse operation'''
    
    START = 0
    STARTOPEN = 1
    FREEOPEN = 2
    FREECLOSE = 3
    BRKT = 4
    BRKTOPEN = 5
    BRKTCLOSE = 6



    
class ScrubberXML:

    '''Scrubber class for XML: removes whitespace and rejects objects of exceeding depth'''
    
    __max_char = 256
    __depth = 16
    __stack = None
    __text = None

    
    def __init__(self, **kwargs):
        dprint(3, "\nScrubberXML::__init__")
        self.__stacks = []
        if "length" in kwargs.keys():
            self.__max_char = kwargs["length"]
        if "depth" in kwargs.keys():
            self.__depth = kwargs["depth"]
        self.__stack = Stack(self.__depth)
        if "text" in kwargs.keys():
            self.parse(kwargs["text"])

            
    def parse(self, text):
        '''Parse XML for whitespace, depth'''
        dprint(3, "\nScrubberXML::parse")
        i = -1
        l = len(text) - 1
        build_str = ""
        free_str = ""
        tag_state = xml.START
        try:
            while i < l :
                i += 1
                next_char = text[i]
                if tag_state == xml.START:
                    if next_char == '<' :
                        tag_state = xml.STARTOPEN
                    build_str += next_char
                    continue
                if tag_state == xml.STARTOPEN:
                    if next_char == '>' :
                        tag_state = xml.FREECLOSE
                    build_str += next_char
                    continue
                if tag_state == xml.FREECLOSE:
                    if next_char == '<' :
                        tag_state = xml.BRKT
                        build_str += next_char
                    continue
                if tag_state == xml.BRKT:
                    if free_str != "":
                        if str.isalnum(next_char) :
                            tag_state = xml.BRKTOPEN
                            self.__stack.push(i)
                            free_str = ""
                            build_str += "<" + next_char
                            continue
                        elif next_char == '/':
                            tag_state = xml.BRKTCLOSE
                            build_str += free_str + next_char
                            free_str = ""
                            self.__stack.pop()
                            continue
                    if str.isalnum(next_char):
                        tag_state = xml.BRKTOPEN
                        self.__stack.push(i)
                    elif next_char == '/' :
                        tag_state = xml.BRKTCLOSE
                        self.__stack.pop()
                    build_str += next_char
                    continue
                if tag_state == xml.BRKTOPEN :
                    if next_char == '>' :
                        tag_state = xml.FREEOPEN
                    build_str += next_char
                    continue
                if tag_state == xml.BRKTCLOSE :
                    if next_char == '>' :
                        tag_state = xml.FREECLOSE
                    build_str += next_char
                    continue
                if tag_state == xml.FREEOPEN :
                    if len(free_str) >= self.__max_char:
                        raise Exception("XML limit exceeded for tag data length")
                    free_str += next_char
                    if next_char == '<' :
                        tag_state = xml.BRKT
                        continue
                    continue
        except Exception as e:
            raise Exception("Scrub failed: " + str(e))
        else:
            self.__text = build_str
            

    def get_parsed(self):
        '''Get parsed text'''
        dprint(3, "\nScrubberXML::get_parsed")
        return self.__text
