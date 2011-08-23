import sys
import locale
import pygtk
import gtk #@UnresolvedImport
import gtk.glade #@UnresolvedImport
from pyCatcherModel import BaseStationInformation
from xdot import DotWidget
import datetime
import time

class PyCatcherGUI:
    
    def __init__(self, catcher_controller):
        encoding = locale.getlocale()[1]
        self._utf8conv = lambda x : unicode(x, encoding).encode('utf8')
        
        self._scan_toggled_on = False
        self._firmware_toggled_on = False
        
        self._catcher_controller = catcher_controller
        
        self._w_tree = gtk.glade.XML("../GUI/mainWindow.glade")        
        
        self._bs_tree_view = self._w_tree.get_widget("bs_table")
        self._add_column("Provider", 0)
        self._add_column("Frequency", 1)
        self._add_column("Strength",2)
        self._add_column("Last seen", 3)
        self._bs_tree_view.set_model(self._catcher_controller.bs_tree_list_data)
              
        self._horizontal_container = self._w_tree.get_widget("vbox4")
        self._dot_widget = DotWidget()
        self._horizontal_container.pack_start_defaults(self._dot_widget)
        self._dot_widget.show()
        
        self._main_window = self._w_tree.get_widget("main_window")
        signals = {"on_main_window_destroy": gtk.main_quit,
                   "on_scan_toggle_toggled": self._on_toggle_scan,
                   "on_firmware_toggle_toggled": self._on_toggle_firmware,
                   "on_graph_zoom_in_clicked": self._dot_widget.on_zoom_in,
                   "on_graph_zoom_out_clicked": self._dot_widget.on_zoom_out,
                   "on_graph_fit_clicked": self._dot_widget.on_zoom_fit,
                   "on_graph_zoom_default_clicked": self._dot_widget.on_zoom_100,
                   "on_save_project_clicked": self._on_save_project,
                   "on_open_file_clicked": self._on_open_file
                   }
        self._w_tree.signal_autoconnect(signals)  
                
        log_view = self._w_tree.get_widget("log_output")
        self._log_buffer = log_view.get_buffer()        
        self._log_buffer.insert(self._log_buffer.get_end_iter(),self._utf8conv("-- Log execution on " + datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M %p") + "  --\n\n"))
        
        self._main_window.show() 
        
        
    def _add_column(self, name, index):
        column = gtk.TreeViewColumn(name, gtk.CellRendererText(), text=index)
        column.set_resizable(True)
        column.set_sort_column_id(index)
        self._bs_tree_view.append_column(column)
        
    def _on_toggle_scan(self, widget):
        if(not self._scan_toggled_on):
            self._catcher_controller.start_scan()
            self._scan_toggled_on = True
        else:
            self._catcher_controller.stop_scan()
            self._scan_toggled_on = False
            
    def _on_toggle_firmware(self, widget):
        if(not self._firmware_toggled_on):
            self._catcher_controller.start_firmware()
            self._firmware_toggled_on = True
        else:
            self._catcher_controller.stop_firmware()
            self._firmware_toggled_on = False
    
    def _on_open_file(self, widget):
        chooser = gtk.FileChooserDialog(title="Open dot File",
                                        action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons=(gtk.STOCK_CANCEL,
                                                 gtk.RESPONSE_CANCEL,
                                                 gtk.STOCK_OPEN,
                                                 gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        filter = gtk.FileFilter()
        filter.set_name("Graphviz dot files")
        filter.add_pattern("*.dot")
        chooser.add_filter(filter)
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        chooser.add_filter(filter)
        if chooser.run() == gtk.RESPONSE_OK:
            filename = chooser.get_filename()
            chooser.destroy()
            self.load_dot_from_file(filename)
        else:
            chooser.destroy()
    
    def load_dot_from_file(self, filename):
        try:
            fp = file(filename, 'rt')
            self.load_dot(fp.read(), filename)
            fp.close()
        except IOError, ex:
            self.show_info(ex)
    
    def load_dot(self, dotcode, filename="<stdin>"):
        if self._dot_widget.set_dotcode(dotcode, filename):
            self._dot_widget.zoom_to_fit()
    
    def _on_save_project(self, widget):
        pass
    
    def show_info(self, message, title='PyCatcher', time_to_sleep=3, type='INFO'):
        gtk_type = {'INFO' : gtk.MESSAGE_INFO,
                    'ERROR': gtk.MESSAGE_ERROR}
        
        dlg = gtk.MessageDialog(type=gtk.MESSAGE_INFO,
                                    message_format=str(message)                                
                                    )
        
        dlg.set_title(title)
        #dlg.run()
        dlg.show()
        time.sleep(time_to_sleep)
        dlg.destroy()
    
    def log_line(self, line):
        self._log_buffer.insert(self._log_buffer.get_end_iter(),self._utf8conv(datetime.datetime.now().strftime("%I:%M:%S %p")+ ":     " + line + "\n"))