# Memobook

Project discontinued. Please see my MemoServ and MemoFace projects, anyone who accidentally found their way to this page.
 -  MemoBook: a notepad/texteditor derivative for people who don't want to remember everything ever.
 -  If you commonly write down things you've learned in plain text files -- because there's just too much to remember --
 -  ...and months later you need that information but can't remember where you wrote it down...
 -  Then sure, you could grep your home directory to death. Or, this is the application for you.

## The Memobook Note Suite:
 -  Includes a Vim plugin, a windowed GUI, a Gedit plugin, and a GNU Emacs plugin.
 -  Can display image and pdf files too (read-only) with basic functionality (zooming, rotating, etc.) -- windowed GUI only.
 -  Stores information (your bookmarks) about the image & pdf files without altering them.
 -  Bookmarks in plaintext files can be tagged in the text itself, or can be "silently" added, i.e., recorded outside of the file

## Why use anything in this suite?
 -  Because grepping for keywords isn't always ideal. You know you best, and you know how you think best. When you write a bit of information down in a file, who knows better than you what words/topics/ideas you'll use to try to find it a year or two from now? And those will be the bookmarks you place in that file so that in a year or two, when you vaguely remember writing a thing or two down, you can find it.
 -  And because you don't want to waste the time using a file format that only one specific application can understand. Memobook Note Suite works with what you already have, use, and maybe even, a little nerdishly, love.

## Dependencies:

### The windowed GUI:
 -  Is written in Python 3; requires tkinter, pillow, and poppler libraries. Pillow (PIL) version 6+ -- must have ImageTk.
 -  As far as I know, the poppler dependency is a deal-breaker for the GUI on Windows.

### The Vim extension:
 -  Requires Vim 8+ (I think)
 -  Currently has an optional Python 3 dependency which can be removed so that it can run on a system having no Python.
 -  Configuration script for Vim currently supports vim-plug and pathogen utilities, as well as Vim 8+ plugin functionality. For other plugin methods, it's currently DIY.

### The GNU Emacs extension:
 -  No longer requires Python 3. Doesn't have any depends except upon version (???) of Emacs.

### The Gedit plugin:
 -  Requires Python 3 and PyGObject. PyGObject must be new enough to have Gtk 3+ and Gedit 3+ submodules.

### All portions:
 -  Require sqlite3. The windowed portion requires Python module sqlite3; the Vim extension requires an sqlite3 binary in the user's $PATH

## Installation and configuration:
 -  Download these files or clone the git repo
 -  Run the config.sh bash script with any desired options
 -  The tag sequence for bookmarks is initially configured in the config.sh script, but can also be manually changed in appropriate files. Grep them to find them.

## Usage: 
 -  In all portions: reading, writing, etc, of files is the same as it always was. However, once a few files have been bookmarked, files may be searched by those bookmarks. 
 -  In all portions: Text files may be bookmarked simply by prefixing a word with the tag sequence. For example, by default the tag sequence is @@. So, in a text file about how to use ffmpeg to transcode a movie file from one codec to another, one might use @@ffmpeg and @@HVEC to make the file searchable by "ffmpeg" or "HVEC".
 -  In all portions: silent bookmarks are not stored in the file itself. Hence, they must be added in a different manner. However, when searching for files by bookmark, nothing special must be done; silent marks will be searched as well.
 -  Windowed GUI: operates much like any other windowed text editor. Use 'Sources' menu for specifying and scanning directories for your existing (if any) bookmarked text files. Scanning will also load (if any) silent marks that are associated with image, pdf, and text files. Under the 'Edit' menu marks may be managed/inserted. To run from the command line, type 'memobook'. Running as a desktop app is currently DIY, but...There's no icon included with these files. (The struggle is real.)
 -  Vim: User preference may vary quite widely, so feel free to edit the plugin/memobook.vim to get desired key mappings. Please see doc/memobook.txt for mappings and command information.
 -  Gedit: Alt-m brings up an open-by-mark dialogue. Under Tools->Memobook are basic options. Please make a special note of the menu items Save (with Marks) amd Save As (with Marks). They are necessary to save mark information into the memobook. These two items will do their memobook magic while Gedit does its own file-saving magic. If a file is saved without them, mark information will not be recorded. I admit this is clumsy, but until I find a better way, this was the best option.
 -  Emacs: in memobook minor mode, all functions begin with alt-m. Then... m (mark search or), Ctrl-m (mark search and), n (add silent mark), Ctrl-n (manage silents), s (scan sources), Ctrl-s (manage sources), c (clear sources).

## Known Problems:
 -  Upgrades to the base distribution can lead to problems with pillow module (pip). Thus far, the best solution has been to uninstall pillow then reinstall it. 

## For the future:
 - [ ]  Rework for Wx, updating Tk interface for compatibility
 - [ ]  Rework the emacs interface.
 - [ ]  Fix UTF-associated problems for text files.
 - [ ]  Better handling of what is a text file and what is not.

Author: Miguel Abele 

License: see file, LICENSE, provided with source code.


