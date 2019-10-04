#!/usr/bin/python3

''' launcher for memobook, albeit poorly named '''


import os
import os.path
from memobook import Memobook


working_path = os.path.dirname(os.environ["_"])
mb = Memobook(ctrl=str(working_path) + os.sep + "conf.xml",index=str(working_path)+os.sep+"index.xml")


mb.root.mainloop()
