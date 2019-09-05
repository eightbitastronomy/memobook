#!/usr/bin/python3

# launcher for memobook, albeit poorly named


from memobook import Memobook


mb = Memobook(ctrl="conf.xml")


mb.root.mainloop()
