#!/usr/bin/python3

# launcher for memobook, albeit poorly named


from memobook import Memobook
import os
import os.path

working_path = os.path.dirname(os.environ["_"])
mb = Memobook(ctrl=str(working_path) + os.sep + "conf.xml")


mb.root.mainloop()
