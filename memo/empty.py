'''Module for printing skeleton conf.xml and index.xml when either is missing'''


def write_skeleton_conf(filepath):
    with open(filepath,"w") as f:
        f.write('''<?xml version="1.0" ?>
<configuration>
   <db>
      <src>archive.db</src>
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
    <loc>.</loc>
    <index>.</index>
    <x>919</x>
    <y>448</y>
  </configuration>''')



def write_skeleton_index(filepath):
    with open(filepath,"w") as f:
        f.write('''<?xml version="1.0" ?>
  <contents>
  </contents>''')
