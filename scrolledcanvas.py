import PIL
import math
import tkinter
import base64
import io
from PIL import Image
from PIL import ImageTk
from tkinter import font



###  PIL does not support SVG; only writes PDF. See https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html




# the images for rotate buttons:

ccw_str = '''R0lGODlhagByAKECAAAAAA0NDf///////yH5BAEKAAIALAAAAABqAHIAAAL+lIBpy+0Po5y0yoStnmD7/2AZGInmqZCqg3br0cbtq8ZgIOd5QG+yrwvqepUcRYhEEktGSPKpXDaCIah1KDVEtdcudpmEPUlXsNdm3r7Op+xUTWan3Czhmk0vfkFnXr6C08TX9eexB0RYiDjzgaeoIQjp+Gjxs+hFKclYKeeSeYSm1/kpisLZ6UnKtHmBiqDKEerkOgdbZdpK+2o7i9urm8rLIPsGHCy8wFoMjHzb5qzbDD1SZyw9XZscff1rUn3Gfeq9PBbuEfisbWe+ohzJTuPLJQKfp1xPeY//iOK3n6nv3x95AhURLDjwIEI6ChdmaegwDb2ICdNRdAPx4p3VcRofWuxIJCPIQRxH9hBp8lK2lDU+soxT8iXMmDINuaypchdOkhN3NrrpExTNoEJ7EhVH7WippEpjDW2K7RjUb0ynRrXq1ChWqiu3ztPqVR3YsGLGeu1HllzXsyihtnULdGtArOjMyn17dC5WvHn5BtVrFTDcuIH9+iTG1jBOxC0vMp4Z8TFPnQIl/3xqzvJlwsgsSdFsy7NHwQBFY4zhz1ZdxTZB23tX0XRs2QYPjYZdmopE26rKbV53zZgVeMLD4CuOux5yu/9W00oN0hXRMmkP4CsAADs='''

cw_str = '''R0lGODlhagByAKECAAAAAA0NDf///////yH5BAEKAAIALAAAAABqAHIAAAL+lI+py+0P4wK0yosjyDzV34XNR5alyJgbKqruS7GCK2MBjONB99ZaDsxhYL5R8BiE4IoKpPNoJDIPzypwIpxat1dq0mcNVWfQmpPJlaKQU0/6tP62m29LKzt/1O+wXT5ywyW29De0xaNWKJHGQai4yGhI83ixV9lDCfl2OZmpVLfy2enpABojqkKKalmKqRplukry2mpqlzJK62Z7S5eqi8XbuwsH7CscSlxsjIA87GXCHIw8PSt9LIxtfV0Nqv3MjbvZrOIXLvmkDHIeJ2fwyw6WmBtfFA29XE8ZmK//SO+vELyAlAYSFGjwYJ6ECucwbKjlHsSFDyeakWixTcXYjCw2cuSz7aM9jCIv9ivZLiTKjiRXglznMqXKmIhO0kQH82bNmTo58ez5wyZQPS2Hyjpl1GfOpEeTMSUq9Ok3p1LF/axKLipWMlq3esT6tWpYqfyubuVq1uvYp2uZtk0K8Ow7E+bkZu0q9q1RvUPjyvWrtqhdwIHxsiWcl29PV3bxGT6HVJ5iXUtlMA74WJNgyJsHIab8OUMibpdHlgYd2rOLuq/KdpZ8uuDoP+4QOspUO+JtUmxM40FdplHva87GsCs+PB7y3f6Wp9Xnmhfrj7b2Gm8841oBADs='''





class ScrolledCanvas(tkinter.Canvas):

    _src = None
    _canvas_ref = None
    _scale = 1.0
    _x = 0
    _y = 0
    _inc_x = 0.
    _inc_y = 0.
    _auto_resize = None
    #__ccw = None
    __ccw_tk = None
    #__cw = None
    __cw_tk = None
    
    def __init__(self,master,**kwargs):
        if "source" in kwargs.keys():
            self._src = kwargs["source"]
            del kwargs["source"]
        else:
            raise Exception("ScrolledCanvas requires a source file for constructor")
        self._frame = tkinter.Frame(master)
        self._ctrl_frame = tkinter.Frame(self._frame,
                                          width=1)
        self._disp_frame = tkinter.Frame(self._frame)
        kwargs.update({"master":self._disp_frame})
        tkinter.Canvas.__init__(self,**kwargs)
        __ccw = Image.open(io.BytesIO(base64.b64decode(ccw_str)))
        self.__ccw_tk = ImageTk.PhotoImage(__ccw.resize((14,14,)))
        self._rotate_CCW_bt = tkinter.Button(self._ctrl_frame,
                                             text="L",
                                             image=self.__ccw_tk,
                                             padx=0,
                                             pady=0,
                                             command=lambda: self._rotate_CCW())
        __cw = Image.open(io.BytesIO(base64.b64decode(cw_str)))
        self.__cw_tk = ImageTk.PhotoImage(__cw.resize((14,14,)))
        self._rotate_CW_bt = tkinter.Button(self._ctrl_frame,
                                            text="R",
                                            image=self.__cw_tk,
                                            padx=0,
                                            pady=0,
                                            command=lambda: self._rotate_CW())
        self._rotate_lbl = tkinter.Label(self._ctrl_frame,
                                         text="Rotate")
        page_filler_0 = tkinter.Label(self._ctrl_frame,
                                      text="   ")
        self._auto_resize = tkinter.IntVar()
        self._auto_resize_cb = tkinter.Checkbutton(self._ctrl_frame,
                                                   text="Auto-resize",
                                                   variable=self._auto_resize,
                                                   onvalue=1,
                                                   offvalue=0,
                                                   padx=0,
                                                   pady=0)

        self._scroll_v = tkinter.Scrollbar(self._disp_frame,
                                           orient="vertical")
        self._scroll_h = tkinter.Scrollbar(self._disp_frame,
                                           orient="horizontal")
        if "OpenSymbol" in tkinter.font.families(root=master):
            self._zoom = tkinter.Label(self._disp_frame,
                                       text="",
                                       borderwidth=0,
                                       padx=0,
                                       pady=0,
                                       font=("Open Symbol",
                                             10,
                                             "normal"))
        else:
            self._zoom = tkinter.Label(self._disp_frame,
                                       text="⃝",
                                       borderwidth=0,
                                       padx=0,
                                       pady=0,
                                       font=("Open Symbol",
                                             10,
                                             "normal"))
        tkinter.Canvas.config(self,
                              yscrollcommand=self._scroll_v.set,
                              xscrollcommand=self._scroll_h.set)
        self._scroll_v.config(command=self.yview)
        self._scroll_h.config(command=self.xview)
        self._rotate_CCW_bt.grid(row=0,
                                 column=9,
                                 sticky="e")
        self._rotate_CW_bt.grid(row=0,
                                column=10,
                                sticky="e")
        self._rotate_lbl.grid(row=0,
                              column=11,
                              sticky="e")
        self._auto_resize_cb.grid(row=0,
                                  column=12,
                                  sticky="e")
        self.grid(row=0,
                  column=0,
                  sticky="nswe")
        self._scroll_v.grid(row=0,
                            column=1,
                            sticky="ns")
        self._scroll_h.grid(row=1,
                            column=0,
                            sticky="we")
        self._zoom.grid(row=1,
                        column=1,
                        sticky="nswe")
        self._ctrl_frame.grid_rowconfigure(0,
                                           weight=0)
        self._ctrl_frame.grid(row=0,
                              column=0,
                              sticky="nwe")
        self._disp_frame.grid_rowconfigure(0,
                                           weight=1)
        self._disp_frame.grid_rowconfigure(1,
                                           weight=0)
        self._disp_frame.grid_columnconfigure(0,
                                              weight=1)
        self._disp_frame.grid(sticky="nswe")
        self._frame.grid_rowconfigure(0,
                                      weight=0)
        self._frame.grid_rowconfigure(1,
                                      weight=1)
        self._frame.grid_columnconfigure(0,
                                         weight=1)
        self._frame.grid(sticky="nswe")
        self._zoom.bind("<Button-1>",lambda e:self._set_zoom())
        self._frame.bind("<Configure>", lambda e: self._on_frame_configure(True))
        self.bind("<Button-1>",lambda e: self._drag_start(e.x,e.y))
        self.bind("<B1-Motion>",lambda e: self._drag(e.x,e.y))
        self.bind("<Button-4>",lambda e: self._wheel(e,-1))
        self.bind("<Button-5>",lambda e: self._wheel(e,1))
        self.bind("<MouseWheel>",lambda e: self._wheel(e))
        canv_meths = vars(tkinter.Canvas).keys()
        methods = vars(tkinter.Pack).keys() | vars(tkinter.Grid).keys() | vars(tkinter.Place).keys()
        methods = methods.difference(canv_meths)
        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self._frame, m))

    def get_frame(self):
        return self._frame

    def set_hook(self,func):
        pass
                
    def __str__(self):
        return str(self._frame)
    
    def _set_zoom(self):
        def __apply_zoom(canv,widge,dia):
            try:
                zoom = float(dia.get())
                if (zoom > 0.) and (zoom <= 500.0):
                    self._scale = zoom/100.0
                    self._resize()
                widge.destroy()
            except Exception as e:
                print(e)
        dialog_win = tkinter.Toplevel(self._frame)
        dialog_frame = tkinter.Frame(dialog_win)
        instructions = tkinter.Label(dialog_frame,text="Zoom (%):")
        dialog = tkinter.Entry(dialog_frame,width=8)
        dialog.insert(0,str(self._scale*100.0))
        dialog_apply = tkinter.Button(dialog_frame,text="Apply",command=lambda:__apply_zoom(self,dialog_win,dialog))
        dialog_win.bind("<Return>",lambda e:dialog_apply.invoke())
        instructions.pack(side="left")
        dialog.pack(side="left")
        dialog_apply.pack(side="left")
        dialog_frame.pack()
        
    def _resize(self):
        pass

    def _rotate_CCW(self):
        pass

    def _rotate_CW(self):
        pass
    
    def _on_frame_configure(self,eventflag):
        '''Reset the scroll region to encompass the inner frame'''
        tkinter.Canvas.configure(self,scrollregion=self.bbox("all"))

    def _drag_start(self,x,y):
        '''Mouse button down; begin drag operation; collect position information'''
        self._x = x
        self._y = y
        bounding = self.bbox(self._canvas_ref)
        self._inc_x = 1./float(bounding[2]-bounding[0])
        self._inc_y = 1./float(bounding[3]-bounding[1])

    def _drag(self,x,y):
        '''Mouse button down while motion detected; drag operation; scroll canvas image'''
        deltax = float(self._x - x)
        deltay = float(self._y - y)
        movex = deltax*self._inc_x + self.xview()[0]
        self.xview_moveto(movex)
        movey = deltay*self._inc_y + self.yview()[0]
        self.yview_moveto(movey)
        self._x = x
        self._y = y

    def _wheel(self,e,direction=0):
        bounding = self.bbox(self._canvas_ref)
        inc = 1./50.
        if direction == 0:
            y = -1.*e.delta*inc + self.yview()[0]
        else:
            y = float(direction)*inc + self.yview()[0]
        self.yview_moveto(y)
        self._y = y
