###############################################################################################
#  empty.py: skeleton xml file utilities
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



'''Module for printing skeleton conf.xml and index.xml when either is missing'''


from memo.debug import dprint


def write_skeleton_conf(path, filepath):
    '''Return string containing contains of skeleton conf.xml'''
    dprint(3, "\nempty.write_skeleton_conf")
    with open(path + filepath, "w") as f:
        f.write('''<?xml version="1.0" ?>
<configuration>
   <db>
      <src>''' + path + '''archive.db</src>
      <table>bookmarks</table>
      <scan>.</scan>
    </db>
    <mime>
      <Text>
        <suff>.txt</suff>
      </Text>
      <Image>
        <suff>.blp</suff>
        <suff>.bmp</suff>
        <suff>.cur</suff>
        <suff>.dcx</suff>
        <suff>.dds</suff>
        <suff>.dib</suff>
        <suff>.eps</suff>
        <suff>.fli</suff>
        <suff>.flc</suff>
        <suff>.fpx</suff>
        <suff>.ftex</suff>
        <suff>.gbr</suff>
        <suff>.gd</suff>
        <suff>.gif</suff>
        <suff>.icns</suff>
        <suff>.ico</suff>
        <suff>.im</suff>
        <suff>.imt</suff>
        <suff>.jpeg</suff>
        <suff>.jpg</suff>
        <suff>.mic</suff>
        <suff>.mpo</suff>
        <suff>.msp</suff>
        <suff>.pcd</suff>
        <suff>.pcx</suff>
        <suff>.pixar</suff>
        <suff>.png</suff>
        <suff>.ppm</suff>
        <suff>.psd</suff>
        <suff>.sgi</suff>
        <suff>.tga</suff>
        <suff>.tiff</suff>
        <suff>.wal</suff>
        <suff>.xbm</suff>
        <suff>.xpm</suff>
      </Image>
      <PDF>
        <suff>.pdf</suff>
      </PDF>
    </mime>
    <font>
      <family>FreeSans</family>
      <size>10</size>
      <weight>normal</weight>
    </font>
    <style>
      <theme>default</theme>
      <font>
        <size>0</size>
      </font>
    </style>
    <wrap>word</wrap>
    <save>.</save>
    <open>.</open>
    <loc>''' + path + filepath + '''</loc>
    <index>''' + path + '''index.xml</index>
    <x>200</x>
    <y>200</y>
  </configuration>''')



def write_skeleton_index(path, filepath):
    '''Return string containing contains of skeleton index.xml'''
    dprint(3, "\nempty.write_skeleton_index")
    with open(path+filepath, "w") as f:
        f.write('''<?xml version="1.0" ?>
  <contents>
  </contents>''')
