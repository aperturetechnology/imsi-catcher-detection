import sys
import pygtk
import gtk #@UnresolvedImport
import gtk.glade #@UnresolvedImport
from driverConnector import DriverConnector
from pyCatcherModel import BaseStationInformation, BaseStationInformationList
from pyCatcherView import PyCatcherGUI
from pyCatcherController import DriverConnector

class PyCatcherController:
    def __init__(self):
        
        self.bs_tree_list_data = gtk.ListStore(str,str,str,str)
                
        self._gui = PyCatcherGUI(self)
        self._driver_connector = DriverConnector()
        
        self._gui.log_line("GUI initialized")
        
        gtk.main()
                
    def log_message(self, message):
        self._gui.log_line(message)            
    
    def start_scan(self):
        self._gui.log_line("start scan")
        
    def stop_scan(self):
        self._gui.log_line("stop scan")
        
    def start_firmware(self):
        self._gui.log_line("start firmware")
        self._driver_connector.start_firmware(self._firmware_waiting_callback, self._firmware_done_callback)
        
    def stop_firmware(self):
        self._gui.log_line("stop firmware")
        print 'stop firmwares'
        self._driver_connector.stop_firmware()
    
    def _found_base_station_callback(self):
        self._gui.log_line("found base station")
    
    def _firmware_waiting_callback(self):
        self._gui.log_line("firmware waiting for device")
        self._gui.show_info('Switch on the phone now.', 'Firmware')
        
 
    def _firmware_done_callback(self):
        self._gui.log_line("firmware loaded, ready for scanning")
        self._gui.show_info('Firmware load completed', 'Firmware')
    