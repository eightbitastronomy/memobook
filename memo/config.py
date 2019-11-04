###############################################################################################
#  config.py: configuration global constants and debug printing
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




######## configuration values ########

TAG_MARKER="@@"
XML_STACK_DEPTH=4
XML_MAX_CHAR=512
TAB_SIZE=8



######## debugging/tracing ########

DEBUG_PRINT=False    # activate printing of debug information
VERBOSITY=3          # 0: no printing;
                     # 1: Exception-error printing
                     # 2: Additional error and other priority printing
                     # 3: Flow-tracing printing

if DEBUG_PRINT:
    import sys

    
def dprint(level,errorstring):
    if DEBUG_PRINT:
        if VERBOSITY >= level:
            sys.stderr.write(errorstring)
            sys.stderr.flush()
    return
