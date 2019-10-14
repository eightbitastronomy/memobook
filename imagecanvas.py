from scrolledcanvas import ScrolledCanvas
from PIL import Image
from PIL import ImageTk




###  PIL does not support SVG; only writes PDF. See https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html



class ImageCanvas(ScrolledCanvas):

    __src_tk = None
    __sz = None
    
    def __init__(self,master,**kwargs):
        ScrolledCanvas.__init__(self,master,**kwargs)
        self.__sz = self._src.size
        self.__src_tk = ImageTk.PhotoImage(self._src)
        self._canvas_ref = self.create_image(0,0,image=self.__src_tk,anchor="nw")
    
    def _resize(self):
        self.__src_tk = ImageTk.PhotoImage(self._src.resize((int(self._scale*float(self.__sz[0])),
                                                              int(self._scale*float(self.__sz[1])))
                                                             ))
        self.itemconfig(self._canvas_ref,image=self.__src_tk)
        self._on_frame_configure(False)

    def _rotate_CCW(self):
        self._src = self._src.rotate(90.0,expand=1)
        self.__sz = (self.__sz[1],self.__sz[0],)
        self._resize()

    def _rotate_CW(self):
        self._src = self._src.rotate(-90.0,expand=1)
        self.__sz = (self.__sz[1],self.__sz[0],)
        self._resize()


    def _on_frame_configure(self,eventflag):
        '''Reset the scroll region to encompass the inner frame'''
        if eventflag and (self._auto_resize.get() == 1):
            self._scale = (self._frame._nametowidget(self._frame.winfo_parent()).winfo_width() - self._scroll_v.winfo_reqwidth()) / self.__sz[0]
            self._resize()
        ScrolledCanvas._on_frame_configure(self,eventflag)

