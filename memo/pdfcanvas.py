###############################################################################################
#  pdfcanvas: canvas class for pdfs
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


'''Scrolled Canvas for PDF documents'''


import tkinter
from tkinter import font
from PIL import ImageTk
from memo.scrolledcanvas import ScrolledCanvas
from memo.debug import dprint




class PDFCanvas(ScrolledCanvas):

    '''PDF-platen display class'''
    
    __src_tk = None  # source pdf, in TkImage container
    __current = 0    # current pdf page image
    __sz = None      # list of (x,y) image sizes
    __pos = None     # list of positions of page images when too large for platen
    

    def __init__(self, master, **kwargs):
        dprint(3, "\nPDFCanvas::__init__")
        ScrolledCanvas.__init__(self, master, **kwargs)
        self.__src_tk = []
        self.__sz = []
        self.__pos = []
        for doc in self._src:
            self.__sz.append(doc.size)
            self.__pos.append([0., 0.])
        self.__page_rev = tkinter.Button(self._ctrl_frame,
                                         text="<",
                                         padx=0,
                                         pady=0,
                                         command=lambda: self.__set_page_rev())
        self.__page_rev_f = tkinter.Button(self._ctrl_frame,
                                           text="<<",
                                           padx=0,
                                           pady=0,
                                           command=lambda: self.__goto(0))
        self.__page_fwd = tkinter.Button(self._ctrl_frame,
                                         text=">",
                                         padx=0,
                                         pady=0,
                                         command=lambda: self.__set_page_fwd())
        self.__page_fwd_f = tkinter.Button(self._ctrl_frame,
                                           text=">>",
                                           padx=0,
                                           pady=0,
                                           command=lambda: self.__goto(len(self._src)-1))
        self.__page_nav = tkinter.Entry(self._ctrl_frame,
                                        width="4")
        self.__page_nav.insert(0, "1")
        page_filler_1 = tkinter.Label(self._ctrl_frame,
                                      text="   ")
        self.__page_nav_pgs = tkinter.Label(self._ctrl_frame,
                                            text="/" + str(len(self._src)))
        self.__page_nav_go = tkinter.Button(self._ctrl_frame,
                                            text="Go",
                                            padx=0,
                                            pady=0,
                                            command=lambda: self.__jumpto(self.__page_nav.get()))
        page_filler_2 = tkinter.Label(self._ctrl_frame,
                                      text="  ")
        self.__page_rev_f.grid(row=0,
                               column=0,
                               sticky="w")
        self.__page_rev.grid(row=0,
                             column=1,
                             sticky="w")
        self.__page_fwd.grid(row=0,
                             column=2,
                             sticky="w")
        self.__page_fwd_f.grid(row=0,
                               column=3,
                               sticky="w")
        page_filler_1.grid(row=0,
                           column=4,
                           sticky="w")
        self.__page_nav.grid(row=0,
                             column=5,
                             sticky="w")
        self.__page_nav_pgs.grid(row=0,
                                 column=6,
                                 sticky="w")
        self.__page_nav_go.grid(row=0,
                                column=7,
                                sticky="w")
        page_filler_2.grid(row=0,
                           column=8,
                           sticky="w")
        # resize pdf image based on current window space
        self._scale = (self._frame._nametowidget(self._frame.winfo_parent()).winfo_width() - self._scroll_v.winfo_reqwidth()) / self.__sz[0][0]
        self.__src_tk = ImageTk.PhotoImage(self._src[self.__current].resize((int(self._scale*float(self.__sz[self.__current][0])),
                                                                             int(self._scale*float(self.__sz[self.__current][1])))))
        self._canvas_ref = self.create_image(0,
                                             0,
                                             image=self.__src_tk,
                                             anchor="nw")
        self.__page_nav.bind("<Return>", lambda e: self.__jumpto(self.__page_nav.get()))
        

    def __set_page_rev(self):
        '''Go to previous page'''
        dprint(3, "\nPDFCanvas::__set_page_rev")
        if self.__current > 0:
            self.__goto(self.__current - 1)

            
    def __set_page_fwd(self):
        '''Go to next page'''
        dprint(3, "\nPDFCanvas::__set_page_fwd")
        if self.__current < len(self._src):
            self.__goto(self.__current + 1)
            

    def _resize(self):
        '''Re-process page image for current (x,y)-sizing and display it'''
        dprint(3, "\nPDFCanvas::_resize")
        self.__src_tk = ImageTk.PhotoImage(self._src[self.__current].resize((int(self._scale*float(self.__sz[self.__current][0])),
                                                                              int(self._scale*float(self.__sz[self.__current][1])))))
        self.itemconfig(self._canvas_ref, image=self.__src_tk)
        self._on_frame_configure(False)

        
    def __set_page(self):
        '''Dialogue for navigation by page number'''
        dprint(3, "\nPDFCanvas::__set_page")
        def __apply_page(canv, widge, dia):
            try:
                page = int(dia.get())-1
                if (page > -1) and (page < len(self._src)):
                    self.__goto(page)
                widge.destroy()
            except Exception as e:
                print(e)
        dialog_win = tkinter.Toplevel(self._frame)
        dialog_frame = tkinter.Frame(dialog_win)
        instructions = tkinter.Label(dialog_frame,
                                     text="Page #:")
        dialog = tkinter.Entry(dialog_frame,
                               width=8)
        dialog.insert(0, str(self._scale+1))
        dialog_apply = tkinter.Button(dialog_frame,
                                      text="Apply",
                                      command=lambda: __apply_page(self,
                                                                   dialog_win,
                                                                   dialog))
        dialog_win.bind("<Return>", lambda e:dialog_apply.invoke())
        instructions.pack(side="left")
        dialog.pack(side="left")
        dialog_apply.pack(side="left")
        dialog_frame.pack()
        

    def __goto(self, page):
        '''Set current page and display it'''
        dprint(3, "\nPDFCanvas::__goto")
        self.__pos[self.__current][0]=self.xview()[0]
        self.__pos[self.__current][1]=self.yview()[0]
        self.__current = page
        self.__src_tk = ImageTk.PhotoImage(self._src[self.__current].resize((int(self._scale*float(self.__sz[self.__current][0])),
                                                                              int(self._scale*float(self.__sz[self.__current][1])))))
        self._canvas_ref = self.create_image(0,
                                             0,
                                             image=self.__src_tk,
                                             anchor="nw")
        self.itemconfig(self._canvas_ref, image=self.__src_tk)
        self.xview_moveto(self.__pos[self.__current][0])
        self.yview_moveto(self.__pos[self.__current][1])
        self.__page_nav.delete(0, tkinter.END)
        self.__page_nav.insert(0, str(self.__current+1))

        
    def __jumpto(self, pagestr):
        '''Middle-man function: check validity of page number before handing off to __goto'''
        dprint(3, "\nPDFCanvas::__jumpto")
        try:
            pg = int(pagestr)
        except:
            return
        else:
            pg -= 1 # Account for first page ... 0 vs 1
            if (pg >= 0) and (pg < len(self._src)):
                self.__goto(pg)

                
    def _rotate_CCW(self):
        '''Rotate pdf page by +90 degrees (CCW)'''
        dprint(3, "\nPDFCanvas::_rotate_CCW")
        self._src[self.__current] = self._src[self.__current].rotate(90.0, expand=1)
        self.__sz[self.__current] = (self.__sz[self.__current][1], self.__sz[self.__current][0],)
        self._resize()
        

    def _rotate_CW(self):
        '''Rotate pdf page by -90 degrees (CW)'''
        dprint(3, "\nPDFCanvas::_rotate_CW")
        self._src[self.__current] = self._src[self.__current].rotate(-90.0, expand=1)
        self.__sz[self.__current] = (self.__sz[self.__current][1], self.__sz[self.__current][0],)
        self._resize()

        
    def _on_frame_configure(self, eventflag):
        '''Reset the scroll region to encompass the inner frame'''
        dprint(3, "\nPDFCanvas::_on_frame_configure")
        if eventflag and (self._auto_resize.get() == 1):
            self._scale = (self._frame._nametowidget(self._frame.winfo_parent()).winfo_width() - self._scroll_v.winfo_reqwidth()) / self.__sz[0][0]
            self._resize()
        ScrolledCanvas._on_frame_configure(self, eventflag)
        

    def _drag(self, x, y):
        '''Drag pdf page to new position using mouse'''
        dprint(3, "\nPDFCanvas::_drag")
        ### to meet inheritance needs, override __drag, call parent.__drag, then set self.__pos, then return
        ScrolledCanvas._drag(self, x, y)
        self.__pos[self.__current][0] = self.xview()[0]
        self.__pos[self.__current][1] = self.yview()[0]
