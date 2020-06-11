###############################################################################################
#  imagecanvas.py: canvas class for images
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



'''Scrolled Canvas for Images'''



from PIL import Image
from PIL import ImageTk
from memo.scrolledcanvas import ScrolledCanvas
from memo.debug import dprint




###  PIL does not support SVG; only writes PDF. See https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html




class ImageCanvas(ScrolledCanvas):

    '''ScrolledCanvas for image files'''
    
    __src_tk = None
    __sz = None

    
    def __init__(self, master, **kwargs):
        dprint(3, "\nImageCanvas::__init__")
        ScrolledCanvas.__init__(self, master, **kwargs)
        self.__sz = self._src.size
        self.__src_tk = ImageTk.PhotoImage(self._src)
        self._canvas_ref = self.create_image(0,
                                             0,
                                             image=self.__src_tk,
                                             anchor="nw")


    def _resize(self):
        '''Resize image in canvas'''
        dprint(3, "\nImageCanvas::_resize")
        self.__src_tk = ImageTk.PhotoImage(self._src.resize((int(self._scale*float(self.__sz[0])),
                                                              int(self._scale*float(self.__sz[1])))
                                                             ))
        self.itemconfig(self._canvas_ref,image=self.__src_tk)
        self._on_frame_configure(False)
        

    def _rotate_CCW(self):
        '''Rotate image 90 in canvas'''
        dprint(3, "\nImageCanvas::_rotate_CCW")
        self._src = self._src.rotate(90.0, expand=1)
        self.__sz = (self.__sz[1], self.__sz[0],)
        self._resize()
        

    def _rotate_CW(self):
        '''Rotate image -90 in canvas'''
        dprint(3, "\nImageCanvas::_rotate_CW")
        self._src = self._src.rotate(-90.0, expand=1)
        self.__sz = (self.__sz[1], self.__sz[0],)
        self._resize()


    def _on_frame_configure(self,eventflag):
        '''Reset the scroll region to encompass the inner frame'''
        dprint(3, "\nImageCanvas::_on_frame_configure")
        if eventflag and (self._auto_resize.get() == 1):
            self._scale = (self._frame._nametowidget(self._frame.winfo_parent()).winfo_width()
                           - self._scroll_v.winfo_reqwidth()) / self.__sz[0]
            self._resize()
        ScrolledCanvas._on_frame_configure(self, eventflag)

