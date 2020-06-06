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




# This is not conf.xml nor are its values found in conf.xml. However, configuration
# scripts need to alter it. It contains a few configuration parameters declared, basically,
# as global variables instead of being placed as node/value items in conf.xml because...
#   ...keeping these values in an extconf object means many objects, from the
#   memobook class down to the note class will have to store references to it. This
#   means...
#      1. Messier code from classes to method calls
#      2. slower runtime execution when dereferencing extconf values
# Also, some of these values are used in extconf.py, so I think they should be kept
# here, all in one place. An exception to this is the values found in debug.py.




######## configuration values ########

TAG_MARKER = "@@"
XML_STACK_DEPTH = 4
XML_MAX_CHAR = 512
TAB_SIZE = 8
