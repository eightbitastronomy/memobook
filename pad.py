#!/usr/bin/python3

''' launcher for memobook, albeit poorly named '''


import os
import os.path
import memo


working_path = os.path.dirname(os.environ["_"])
mb = memo.memobook.Memobook(ctrl=str(working_path) + os.sep + "conf.xml",index=str(working_path)+os.sep+"index.xml")


mb.root.mainloop()
