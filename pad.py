#!/usr/bin/python3


###############################################################################################
#  pad.py: standalone loader for memobook
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


''' launcher for memobook, albeit poorly named '''


import os
import os.path
import memo

working_path = os.path.dirname(os.environ["_"])
cctrll = "./conf.xml"
ddexx = "./index.xml"

mb = memo.tkmemobook.TkMemobook(ctrl=cctrll,index=ddexx)


mb.root.mainloop()
