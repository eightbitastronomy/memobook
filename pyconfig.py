import sys
import os
import subprocess
from subprocess import CalledProcessError

fail = False
installs = []


def print_and_abort():
    print("Module check failed")
    sys.exit(-1)


print("Checking modules for Memobook Note Suite for usage...")



try:
    import tkinter
except:
    fail = True
    sys.stderr.write("tkinter module not found\n")

try:
    import sqlite3
except:
    fail = True
    sys.stderr.write("sqlite3 module not found\n")

try:
    import xml.dom.minidom
except:
    fail = True
    sys.stderr.write("xml.dom.minidom module not found\n")

if fail:
    print_and_abort()

    
print("Checking PyPI modules...")

try:
    from PIL import ImageTk # it appears that only vers. >= 6 has ImageTk
                            # so if this fails, vers < 6 was found
except:
    sys.stderr.write("pillow module version >= 6.0 not found\n")
    installs.append("pillow")

try:
    import magic
except:
    sys.stderr.write("file-magic module not found\n")
    installs.append("file-magic")

try:
    import pdf2image
except:
    sys.stderr.write("pdf2image module not found\n")
    installs.append("pdf2image")


    
if installs:
    print("Would you like this script to attempt to install the following modules with pip?")
    print(", ".join(installs))
    answer = input("Yes(y)/No(n)?")
    if answer == 'y':
        try:
            print("Calling 'python3 -m pip install user " + " ".join(installs) + "'...")
            comp_proc = subprocess.run(["python3","-m","pip","install","--user",*installs],capture_output=False,encoding="ascii")
            comp_proc.check_returncode()
            if comp_proc.stderr:
                raise CalledProcessError("Error: pip output: " + comp_proc.stderr)
            installs = [ ]
        except CalledProcessError as cpe:
            print("Error in pip install: " + str(cpe))
        except Exception as e:
            print("Error: " + str(e))
    else:
        print_and_abort()

if installs:
    print_and_abort()



print("Module checking and installation complete")
sys.exit(0)
