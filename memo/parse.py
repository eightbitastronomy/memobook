###############################################################################################
#  parse.py: tag/mark parsing utilities
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




# Parsing and splitting utility functions for text-processing



from memo.config import TAG_MARKER
from memo.debug import dprint



def parse(t):
    '''Parse string for bookmarks. Returns list of results.'''
    dprint(3, "\nparse.parse")
    if t is None:
        return []
    if t is "":
        return []
    tags = []
    working_strings = t.splitlines()
    try:
        while working_strings.index(''):
            working_strings.remove('')
    except:
        pass
    for line in working_strings:
        while (True):
            index = line.find(TAG_MARKER)
            if index < 0 :
                break
            line = line[index+len(TAG_MARKER):]
            temp_str = line.split(' ').pop(0)
            tags.append(temp_str.rstrip("\t"))
            line = line[len(temp_str):]
    return tags


def split_by_unknown(t):
    '''Split string by several possible separators: space, comma, semi-colon, tag-marker, or vertical bar'''
    dprint(3, "\nparse.split_by_unknown")
    if t is None:
        return []
    if t is "":
        return []
    tags = []
    maxpair = ("", 0)
    results = []
    splitters = (" ", ",", ";", TAG_MARKER, "|", ) # not all non-alphanumeric characters are here b/c tags should be mostly unrestricted in form.
    for s in splitters:
        tmp_list = t.split(s)
        results.append((s, len(tmp_list)))
    for pair in results:
        if pair[1] > maxpair[1]:
            maxpair = pair
    working_list = []
    if maxpair[1] == 0:
        # no split found
        return t
    working_list = t.split(maxpair[0])
    try:
        while working_list.index('') > -1:
            working_list.remove('')
    except:
        pass
    finally:
        tags = []
        for item in working_list:
            for s in splitters:
                item = item.strip(s)
            tags.append(item)
        return tags
