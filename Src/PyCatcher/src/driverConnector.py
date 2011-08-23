from pyCatcherModel import BaseStationInformation
import subprocess
import threading 
import re
from pyCatcherSettings import Commands
import sys
import time
import gtk #@UnresolvedImport

class DriverConnector:        
    def __init__ (self):
        self._scan_thread_break = False
        self._firmware_thread_break = False
        self._firmware_waiting_callback = None
        self._firmware_loaded_callback = None
        self._test_thread = None
        
    def start_scanning (self):
        self._scan_thread_break = False
        threading.Thread(target= self._do_scan).start()

    def start_firmware(self, firmware_waiting_callback, firmware_loaded_callback):
        self._firmware_thread_break = False
        self._firmware_waiting_callback = firmware_waiting_callback
        self._firmware_loaded_callback = firmware_loaded_callback      
        testThread = FirmwareThread(self._firmware_waiting_callback, self._firmware_loaded_callback, self._firmware_thread_break)
        testThread.start()
        
    def stop_scanning (self):
        self._scan_thread_break = True
        
    def stop_firmware(self):
        self._firmware_thread_break = True
        
class FirmwareThread(threading.Thread):
    def __init__(self, firmware_waiting_callback, firmware_loaded_callback, thread_break):
        gtk.gdk.threads_init()
        threading.Thread.__init__(self)
        self._firmware_waiting_callback = firmware_waiting_callback
        self._firmware_loaded_callback = firmware_loaded_callback
        self._thread_break = thread_break
       
    def run(self):
        loader_process_object = subprocess.Popen(Commands['osmocon_command'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        time.sleep(3)
        self._firmware_waiting_callback()
        while not self._thread_break:
            line = loader_process_object.stdout.readline()
            #if line:
            #    print line
            if (line.strip() == 'Finishing download phase'):
                self._firmware_loaded_callback()
            #time.sleep(0.5)
        loader_process_object.kill()

class ScanThread(threading.Thread):
        def __init__(self, thread_break):
            gtk.gdk.threads_init()
            threading.Thread.__init__(self)
            self._thread_break = thread_break
        
        def run(self):
            scan_command = Commands['scan_command']
            scan_process = subprocess.Popen(scan_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            while not self._scan_thread_break:
                base_station_info = BaseStationInformation()
                base_station_info.parse_file(scan_process.stdout)
                self._bs_found_callback(base_station_info)
            scan_process.kill()
    