#!/usr/bin/env python

import yaml
import subprocess
import re
import os
import logging

import gi
gi.require_version("Gtk", "3.0")  # @UndefinedVariable
from gi.repository import Gtk  # @UnresolvedImport

from os.path import expanduser


class encfsgui(object):
  configFile = "./conf/encfsgui.yaml"

  def getSelectedName(self):
    return self.getSelectedColumn(1)

  def getSelectedOrigin(self):
    return self.getSelectedColumn(2)

  def getSelectedMount(self):
    return self.getSelectedColumn(3)

  def getSelectedColumn(self, column):
    # Get the TreeView selected row(s)
    selection = self.cargoList.get_selection()
    # get_selected_rows() returns a tuple
    # The first element is a ListStore
    # The second element is a list of tree paths
    # of all selected rows
    model, paths = selection.get_selected_rows()
    
    # Get the TreeIter instance for each path
    for path in paths:
      myIter = model.get_iter(path)
      return  model.get_value(myIter, column)
    
  def on_quit_activate(self, widget, data=None):
    Gtk.main_quit()
    return True
    
  def on_window_destroy(self, widget, data=None):
    Gtk.main_quit()
    return True
    
  def newCargo_clicked_cb(self, widget, data=None):
    self.newName.set_text("")
    # Poner $HOME
    self.newSecretCargoDir.set_filename(expanduser("~"))
    self.newMountPointDir.set_filename(expanduser("~"))    
    self.newCargoWindow.show_all()
        
  def deleteCargo_clicked_cb(self, widget, data=None):
    self.checkCargoState()
    if self.getSelectedName() in self.activeMount:
      logging.debug("Can not delete connected cargo!!")
    else:
      self.deleteCargoDialog.show_all()
        
  def editCargo_clicked_cb(self, widget, data=None):
    self.checkCargoState()
    logging.debug(self.getSelectedName())
    logging.debug(self.getSelectedOrigin())
    logging.debug(self.getSelectedMount())
    if self.getSelectedName() in self.activeMount:
      logging.debug("Can not edit connected cargo!!")
    else:
      self.editName.set_text(self.getSelectedName())
      self.editSecretCargoDir.set_filename(self.getSelectedOrigin())
      self.editMountPointDir.set_filname(self.getSelectedMount())
      self.editCargoWindow.show_all()
    logging.debug("edit cliked!")

  def connectCargo_clicked_cb(self, widget, data=None):
    self.checkCargoState()
    if self.getSelectedName() in self.activeMount:
      logging.debug("Already connected!!!")
    else:
      self.passwdDialogText.set_text("")
      self.passwdDialog.show_all()        
    logging.debug("connect cliked! on %s", self.getSelectedName())
    
  def disconnectCargo_clicked_cb(self, widget, data=None):
    self.checkCargoState()
    if not self.getSelectedName() in self.activeMount:
      logging.debug("Not connected!!! %s", self.getSelectedMount())
    else:
      with open(os.devnull, 'w') as FNULL:
        cmd="fusermount"
        retCode=subprocess.call([cmd, "-u", self.getSelectedMount()], stdout=FNULL, stderr=subprocess.STDOUT)
        logging.debug("%s disconnected with code %s", self.getSelectedMount(), retCode)
    logging.debug("disconnect clicked!")
    self.checkCargoState()
    

  def on_cargoList_row_selected(self, widget, data=None):
    self.checkCargoState()
    logging.debug("list selected!")
    
  def passwordEntry_activate_cb(self, widget, data=None):
    clave=self.passwdDialogText.get_text()
    self.passwdDialog.hide()        
    ##logging.debug("provided password[%s]", clave)
    echoCmd = "echo"
    echoOut = subprocess.Popen([echoCmd,clave],
                               stdout=subprocess.PIPE)
    encfsCmd =["encfs"]
    if (not self.readyCargos.has_key(self.getSelectedName())):
      encfsCmd.append("--paranoia")
    encfsCmd.append(os.path.realpath(self.getSelectedOrigin()))
    encfsCmd.append(os.path.realpath(self.getSelectedMount()))
    subprocess.Popen(encfsCmd,            
          stdin=echoOut.stdout).communicate()
    echoOut.stdout.close()
    self.checkCargoState()
    self.passwdDialogText.set_text("")    

    
  def addNew_clicked_cb(self, widget, data=None):
    logging.debug("Name [%s] SCD[%s] MPD[%s]", self.newName.get_text(), self.newSecretCargoDir.get_filename(), self.newMountPointDir.get_filename())
    self.newCargoWindow.hide()
    self.model.append(["notChecked", self.newName.get_text() , self.newSecretCargoDir.get_filename(), self.newMountPointDir.get_filename()])
    self.saveConfig()
    self.checkCargoState()

  def confirmEdit_clicked_cb(self, widget, data=None):
    logging.debug("Name [%s] SCD[%s] MPD[%s]", self.editName.get_text(), self.editSecretCargoDir.get_filename(), self.editMountPointDir.get_filename())
    self.editCargoWindow.hide()
    self.doDelete()
    self.model.append(["notChecked", self.editName.get_text() , self.editSecretCargoDir.get_filename(), self.editMountPointDir.get_filename()])
    self.saveConfig()
    
  def cancelEdit_clicked_cb(self, widget, data=None):
    logging.debug("cancelEditPressed")
    self.editCargoWindow.hide()  
    
  def cancelNew_clicked_cb(self, widget, data=None):
    logging.debug("cancelNewPressed")
    self.newCargoWindow.hide()    

  def deleteCancel_clicked_cb(self, widget, data=None):
    logging.debug("canceledPressed")
    self.deleteCargoDialog.hide()

  def deleteConfirm_clicked_cb(self, widget, data=None):
    logging.debug("deletePressed")
    self.deleteCargoDialog.hide()
    self.doDelete()    
    logging.debug("delete cliked!")        

  def doDelete(self):
    # Get the TreeView selected row(s)
    selection = self.cargoList.get_selection()
    # get_selected_rows() returns a tuple
    # The first element is a ListStore
    # The second element is a list of tree paths
    # of all selected rows
    model, paths = selection.get_selected_rows()
      
    # Get the TreeIter instance for each path
    for path in paths:
      myIter = model.get_iter(path)
      # Remove the ListStore row referenced by iter
      model.remove(myIter)
    self.saveConfig()

  def activateButtons(self, builder):
    boton = builder.get_object("newCargo")
    boton.set_sensitive(True)
    boton = builder.get_object("editCargo")
    boton.set_sensitive(True)
    boton = builder.get_object("deleteCargo")
    boton.set_sensitive(True)
    boton = builder.get_object("connectCargo")
    boton.set_sensitive(True)
    boton = builder.get_object("disconnectCargo")
    boton.set_sensitive(True)

  def saveConfig(self):
    with open(encfsgui.configFile, "w") as yamlFile:
      dictFile = dict()      
      for row in self.model:
        dictRow = dict()
        dictRow["secret"] = row[2]
        dictRow["clear"] = row[3]
        dictFile[row[1]] = dictRow
      yaml.dump(dictFile, yamlFile)
      
  def loadConfig(self):
    with open(encfsgui.configFile, "r") as yamlFile:
      cfg = yaml.load(yamlFile, Loader=yaml.FullLoader)
      for key, value in cfg.items():
        self.model.append(["notChecked", key, value["secret"], value["clear"]])
    self.checkCargoState()
  
  def checkCargoIsReady(self, origin2Check):
    cmd = "encfsctl"
    with open(os.devnull, 'w') as FNULL:
      retCode = subprocess.call([cmd, origin2Check], stdout=FNULL, stderr=subprocess.STDOUT)
    return retCode
  
  def checkCargoState(self):
    cmd = "mount"
# no block, it start a sub process.
    p = subprocess.Popen(cmd , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#  and you can block util the cmd execute finish
# p.wait()
    stdout, stderr = p.communicate()
    logging.debug("Mounted out\n")
    logging.debug(stdout)
    logging.debug("ERR?")
    logging.debug(stderr)
    mounts = re.findall("encfs on (.*) type fuse.encfs", stdout, re.MULTILINE)
    for row in self.model:
      pathToCheck = os.path.realpath(row[3])
      # TODO translate path to real path
      logging.debug("Checking[%s]\t[%s]\t[%s]" % (row[1], row[3], pathToCheck))      
      alreadyMounted = False
      for mount in mounts:
        logging.debug("\t..%s", mount)
        if pathToCheck == mount:
          alreadyMounted = True
          break
                   
      if alreadyMounted:
        logging.debug("%s mounted", row[3])
        row[0] = "mounted"
        self.activeMount[row[1]] = "on"
        self.readyCargos[row[1]] = "ready"
      else:
        logging.debug("%s NOT mounted", row[3])
        if self.checkCargoIsReady(os.path.realpath(row[2])):
          row[0] = "notReady"
          if self.readyCargos.has_key(row[1]):
            self.readyCargos.pop(row[1])
          if self.activeMount.has_key(row[1]):
            self.activeMount.pop(row[1])                      
        else:
          row[0] = "unmounted"
          self.readyCargos[row[1]] = "ready"
          if self.activeMount.has_key(row[1]):
            self.activeMount.pop(row[1])

  def __init__(self):    
    self.activeMount = dict()
    self.readyCargos = dict()
    builder = Gtk.Builder()
    builder.add_from_file("encfsgui.glade")
    builder.connect_signals(self)
    
    self.activateButtons(builder)
    self.cargoList = builder.get_object("cargoList")
    self.cargoList.set_visible(True)    
    self.model = self.cargoList.get_model()
    self.window = builder.get_object("window")
    self.passwdDialog = builder.get_object("passwordDialog")
    self.passwdDialogText = builder.get_object("passwordEntry")
    self.lastPassword = ""
    self.newCargoWindow = builder.get_object("newCargoWindow")
    self.newName = builder.get_object("newCargoName")              
    self.newSecretCargoDir = builder.get_object("newSecretCargoDir")              
    self.newMountPointDir = builder.get_object("newMountPointDir")
    self.deleteCargoDialog = builder.get_object("deleteDialog")
    self.editCargoWindow = builder.get_object("editCargoWindow")
    self.editName = builder.get_object("editCargoName")              
    self.editSecretCargoDir = builder.get_object("editSecretCargoDir")              
    self.editMountPointDir = builder.get_object("editMountPointDir")

    self.loadConfig()
    self.window.show_all()
    

if __name__ == "__main__":
  FORMAT = '%(asctime)-15s -12s %(levelname)-8s %(message)s'
  formatter = logging.Formatter(FORMAT)
  
  handler = logging.StreamHandler()
  handler.setFormatter(formatter)
  
  logger = logging.getLogger()  
  logger.addHandler(handler)
  logger.setLevel(logging.DEBUG)  

  app = encfsgui()
  Gtk.main()
