###############################################################################################
#  memobookns.py: the GEdit plugin interface
#
#  Author (pseudonomously): eightbitastronomy (eightbitastronomy@protonmail.com)
#  Copyrighted by eightbitastronomy, 2019.
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
#
#  For license and copyright information for Gedit, Gtk, or PyGObject, please refer to
#  documentation and files appropriate to the respective application and/or module.
###############################################################################################


import gi
gi.require_version('Gedit', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gtk, Gedit, Gio
import sys
import importlib.util
spec = importlib.util.spec_from_file_location("memo", "./memo/__init__.py")
memo = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = memo
spec.loader.exec_module(memo)




try:
    import gettext
    gettext.bindtextdomain('gedit')
    gettext.textdomain('gedit')
    _ = gettext.gettext
except:
    _ = lambda s: s
        



mb = None




    
class MNSAppActivatable(GObject.Object, Gedit.AppActivatable):
    app = GObject.Property(type=Gedit.App)
    __gtype_name__ = "MNSAppActivatable"
    menu_ext = []
    menu_items = []
    sub_menu_items = []
    
    def __init__(self):
        GObject.Object.__init__(self)
        global mb
        memo.config.dprint(3,"\nMNSApp init")
        if not mb:
            mb = memo.gmemobook.gMemobook(ctrl="./conf.xml")
            memo.config.dprint(3,"...Memobook initialized")

        
    def do_activate(self):
        memo.config.dprint(3,"\nMNSApp do_activate")
        self._build_menu()
        
        
    def _build_menu(self):
        memo.config.dprint(3,"\nMNSApp _build_menu")
        #self.app.add_accelerator("<Primary><Alt>O", "win.open_by_mark", None)
        menu_ext  = self.extend_menu("file-section")
        self.menu_items.append(Gio.MenuItem.new(_("Open by mark"), "win.open_by_mark"))
        self.menu_items.append(Gio.MenuItem.new(_("Save (with marks)"), "win.save_with_mark"))
        self.menu_items.append(Gio.MenuItem.new(_("Save As (with marks)"), "win.save_as_with_mark"))
        for item in self.menu_items:
            menu_ext.append_menu_item(item)
        self.menu_ext.append(menu_ext)
        menu_ext = self.extend_menu("tools-section")
        sub_menu = Gio.Menu()
        self.sub_menu_items.append(Gio.MenuItem.new(_("Open by mark"), 'win.open_by_mark'))
        self.sub_menu_items.append(Gio.MenuItem.new(_("Silent marks"),'win.silent'))
        self.sub_menu_items.append(Gio.MenuItem.new(_("Scan"),'win.scan'))
        self.sub_menu_items.append(Gio.MenuItem.new(_("Clear"),'win.clear'))
        self.sub_menu_items.append(Gio.MenuItem.new(_("Manage"),'win.manage'))
        for sitem in self.sub_menu_items:
            sub_menu.append_item(sitem)
        menu_ext.append_menu_item(Gio.MenuItem.new_submenu(_("Memobook"), sub_menu))
        self.menu_ext.append(menu_ext)
        self.app.set_accels_for_action("win.open_by_mark", ("<Alt>m", None))
        
    def do_deactivate(self):
        global mb
        memo.config.dprint(3,"\nMNSApp do_deactivate")
        self._remove_menu()
        mb.exit_all(None)
        
    def _remove_menu(self):
        memo.config.dprint(3,"\nMNSApp _remove_menu")
        # removing accelerator and destroying menu items
        self.app.set_accels_for_action("win.open_by_mark", ())
        self.menu_ext = None
        self.menu_items = None
        self.sub_menu_items = None
        
        

class MNSWindowActivatable(GObject.Object, Gedit.WindowActivatable):
    window = GObject.Property(type=Gedit.Window)
    __gtype_name__ = "MNSWindowActivatable"
    __mb_hook = None
    
    def __init__(self):
        GObject.Object.__init__(self)
        global mb
        memo.config.dprint(3,"\nMNSWindow init")
        self.__mb_hook = mb.add_window_hook(self.window)
        
    def do_update_state(self):
        memo.config.dprint(3,"\nMNSWindow do_update_state")
        if self.window.get_active_view() is not None:
            self.window.lookup_action('open_by_mark').set_enabled(True)
            
    def do_activate(self):
        memo.config.dprint(3,"\nMNSWindow do_activate")
        self._connect_menu()
        
    def _connect_menu(self):
        memo.config.dprint(3,"\nMNSWindow _connect_menu")
        refs = ( ('open_by_mark', self.__hook_open_mark),
                 ('save_with_mark', self.__hook_save),
                 ('save_as_with_mark', self.__hook_save_as),
                 ('silent', self.__hook_silent),
                 ('scan', lambda a,d: mb.data.populate()),
                 ('clear', lambda a,d: mb.data.clear()),
                 ('manage', self.__hook_manage),)
        for ref in refs:
            action = Gio.SimpleAction(name=ref[0])
            action.connect('activate', ref[1])
            self.window.add_action(action)

        
    def __hook_open_mark(self, action, data):
        global mb
        memo.config.dprint(3,"\nMNSWindow __hook_open_mark")
        mb.select_window_hook(self.window)
        mb.open_mark()


    def __hook_save(self, action, data):
        global mb
        memo.config.dprint(3,"\nMNSWindow __hook_save")
        mb.select_window_hook(self.window)
        mb.save_note()


    def __hook_save_as(self, action, data):
        global mb
        memo.config.dprint(3,"\nMNSWindow __hook_save")
        mb.select_window_hook(self.window)
        mb.save_note_as()


    def __hook_manage(self, action, data):
        global mb
        memo.config.dprint(3,"\nMNSWindow __hook_manage")
        mb.select_window_hook(self.window)
        mb.open_pop(mb.open_pop_remove,mb.open_pop_add,mb.open_pop_apply)


    def __hook_silent(self, action, data):
        global mb
        memo.config.dprint(3,"\nMNSWindow __hook_silent")
        mb.select_window_hook(self.window)
        mb.mark_dialogue()

        
    def do_deactivate(self):
        memo.config.dprint(3,"\nMNSWindow do_deactivate")

        
    def do_create_configure_widget(self):
        memo.config.dprint(3,"\nMNSWindow do_create_configure_widget")
        box=Gtk.Box()
        box.add(Gtk.Label("Settings? Use Scan, Clear, and Manage. Email eightbitastronomy@protonmail.com if this plugin isn't working."))
        return box


