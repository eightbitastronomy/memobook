import sys
import os
import subprocess
from subprocess import CalledProcessError

fail = False


def print_and_abort():
    print("Module check failed")
    sys.exit(-1)


print("Checking modules for usage of Gedit plugin...")



try:
    import gi
except:
    fail = True
    sys.stderr.write("pygobject module not found\n")

try:
    gi.require_version('Gtk', '3.0')
    from gi.repository import GObject, Gtk, Gio
except:
    fail = True
    sys.stderr.write("pygobject must be updated to contain Gtk 3+")


if fail:
    print("Would you like this script to attempt to install the PyGObject module with pip?")
    answer = input("Yes(y)/No(n)?")
    if answer == 'y':
        try:
            print("Calling 'python3 -m pip install --user pygobject --upgrade'...")
            comp_proc = subprocess.run(["python3","-m","pip","install","--user","pygobject","--upgrade"],capture_output=False,encoding="ascii")
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


print("Gedit module checking and installation complete")
sys.exit(0)
