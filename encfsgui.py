#!/usr/bin/env python
# encoding: utf-8
'''
encfsgui -- GUI for mounting and unmounting encfs directories aka Cargo in this program

This program is graphical frontend for encfs directories os Cargos

@author:     Andrés Caner

@copyright:  2020 Personal. All rights reserved.

@license:    Apache License 2.0

@contact:    bugarnir@gmail.com
@deffield    updated: __date__
'''

import yaml
import subprocess
import re
import logging

import gi
gi.require_version("Gtk", "3.0")  # @UndefinedVariable
from gi.repository import Gtk  # @UnresolvedImport



from os.path import expanduser

from widgetHandlers.messageArea import messageArea
import sys
import os

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

import gettext
#not needed it will be redifined
#from gettext import gettext as _

__all__ = []
__version__ = 0.1
__date__ = '2020-03-17'
__updated__ = '2020-05-22'


class encfsgui(object):
  
  ICON_NOT_READY = "document-new"
  ICON_CHECKING_PENDING = "help-faq"
  ICON_MOUNTED = "network-wired"
  ICON_NOT_MOUNTED = "network-offline"
  GLADEFILENAME="/encfsgui.glade"  

  def getSelectedName(self):
    return self.getSelectedColumn(1)

  def getSelectedOrigin(self):
    return self.getSelectedColumn(2)

  def getSelectedMount(self):
    return self.getSelectedColumn(3)

  def getSelectedColumn(self, column):
    # Get the TreeView selected row(s)
    selection = self.cargoList.get_selection()
    if (selection == None):
      return None
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
  def on_cargoList_row_activated(self, widget, data=None, moreData=None ):
    self.messageArea.addInProgress(_("Changing state of {}").format(self.getSelectedName()))
    logging.debug("double click! on %s", self.getSelectedName())
    self.checkCargoState()
    if (self.activeMount.has_key(self.getSelectedName())):
      self.disconnectCargo_clicked_cb(None, None)
    else:
      self.connectCargo_clicked_cb(None, None)
    
  def newCargo_clicked_cb(self, widget, data=None):
    self.messageArea.addInProgress(_("Defining new Cargo"))
    self.newName.set_text("")
    # Poner $HOME
    self.newSecretCargoDir.set_filename(expanduser("~"))
    self.newMountPointDir.set_filename(expanduser("~"))    
    self.newCargoWindow.show_all()
        
  def deleteCargo_clicked_cb(self, widget, data=None):
    self.messageArea.addInProgress(_("Deleting Cargo {}").format(self.getSelectedName()))
    self.checkCargoState()
    if ( self.getSelectedName() == None):
      logging.debug("Must select a row to be deleted")
      self.messageArea.addError(_("Select a cargo to delete"))
      return
    if self.getSelectedName() in self.activeMount:
      logging.debug("Can not delete connected cargo!!")
      self.messageArea.addError(_("Can not delete connected cargo! {}").format(self.getSelectedName()));
    else:
      self.deleteCargoDialog.show_all()
        
  def editCargo_clicked_cb(self, widget, data=None):
    self.messageArea.addInProgress(_("Editing Cargo {}").format(self.getSelectedName()))
    self.checkCargoState()
    logging.debug(self.getSelectedName())
    logging.debug(self.getSelectedOrigin())
    logging.debug(self.getSelectedMount())
    if ( self.getSelectedName() == None):
      logging.debug("Must select a row to be edited")
      self.messageArea.addError(_("Select a cargo to edit"))
      return
    
    if self.getSelectedName() in self.activeMount:
      logging.debug("Can not edit connected cargo!!")
      self.messageArea.addError(_("Can not edit connected cargo!! {}").format(self.getSelectedName()))
    else:
      self.editName.set_text(self.getSelectedName())
      self.editSecretCargoDir.set_filename(self.getSelectedOrigin())
      self.editMountPointDir.set_filname(self.getSelectedMount())
      self.editCargoWindow.show_all()
    logging.debug("edit cliked!")
    
  def passwordDialogMount_close_cb(self, widget, data=None):
    logging.debug("Mount aborted by user")
    self.messageArea.addOK(_("Mount aborted by user"))


  def passwordDialogNewCargo_close_cb(self, widget, data=None):
    logging.debug("Define and Mount aborted by user")
    self.messageArea.addOK(_("Define and mount aborted by user"))

  def entryPasswordEntryNewCargoFirst(self, widget, data=None):
    self.passwordEntryNewCargoSecond.grab_focus()
        

  def connectCargo_clicked_cb(self, widget, data=None):
    self.checkCargoState()
    logging.debug("connect cliked! on %s", self.getSelectedName())    
    if self.getSelectedName() in self.activeMount:
      logging.debug("Already connected!!!")
      self.messageArea.addError(_("Already connected!!! {}").format(self.getSelectedName()))      
    else:
      if self.getSelectedName() in self.readyCargos:
        self.messageArea.addInProgress(_("Connecting Cargo {}").format(self.getSelectedName()))        
        self.passwdDialogText.set_text("")
        self.passwdDialogMount.show_all()        
      else:
        self.messageArea.addInProgress(_("Initializing and Connecting new Cargo {}").format(self.getSelectedName()))        
        self.passwordEntryNewCargoFirst.set_text("")
        self.passwordEntryNewCargoSecond.set_text("")
        self.passwdDialogNewCargo.show_all()
               
    
  def disconnectCargo_clicked_cb(self, widget, data=None):
    self.messageArea.addInProgress(_("Disconnecting Cargo {}").format(self.getSelectedName()))
    self.checkCargoState()
    if not self.getSelectedName() in self.activeMount:
      logging.debug("Not connected!!! %s", self.getSelectedMount())
      self.messageArea.addError(_("Not connected!!! {}").format(self.getSelectedName()))
    else:
      with open(os.devnull, 'w') as FNULL:
        cmd="fusermount"
        retCode=subprocess.call([cmd, "-u", self.getSelectedMount()], stdout=FNULL, stderr=subprocess.STDOUT)
        logging.debug("%s disconnected with code %s", self.getSelectedMount(), retCode)
    logging.debug("disconnect clicked!")
    self.checkCargoState()
    self.messageArea.addOK(_("Disconnected Cargo {}").format(self.getSelectedName()))
    

  def on_cargoList_row_selected(self, widget, data=None):
    self.messageArea.addInProgress(_("Row Selected ").format(self.getSelectedName()))
    self.checkCargoState()
    logging.debug("list selected!")
    

  def doMountNewCargo(self, clave):
    #logging.debug("provided password[%s]", clave)
    echoCmd = "echo"
    echoOut = subprocess.Popen([echoCmd, clave], stdout=subprocess.PIPE)
  #logging.debug("echo Command [{}]/[{}]".format(echoCmd,clave))
    encfsCmd = ["encfs", "--stdinpass"]
    if (not self.readyCargos.has_key(self.getSelectedName())):
      encfsCmd.append("--paranoia")
    encfsCmd.append(os.path.realpath(self.getSelectedOrigin()))
    encfsCmd.append(os.path.realpath(self.getSelectedMount()))
    logging.debug("encfs Command {}".format(encfsCmd))
    encfsOut, encfsErr = subprocess.Popen(encfsCmd, stdin=echoOut.stdout, stderr=subprocess.PIPE, stdout=subprocess.PIPE).communicate()
    logging.debug("Enfcs Output {}".format(encfsOut))
    logging.debug("Enfcs ErrorOut {}".format(encfsErr))
    echoOut.stdout.close()
    self.checkCargoState()
    if (self.activeMount.has_key(self.getSelectedName())):
      self.messageArea.addOK(_("Cargo mounted! {}").format(self.getSelectedName()))
    else:
      self.messageArea.addError(_("Cannot mount! {}").format(self.getSelectedName()))
      
  def entrypasswordEntryNewCargoSecond(self, widget, data=None):
    clave1st=self.passwordEntryNewCargoFirst.get_text()
    clave2nd=self.passwordEntryNewCargoSecond.get_text()
    self.passwdDialogNewCargo.hide()
    self.passwordEntryNewCargoFirst.set_text("")
    self.passwordEntryNewCargoSecond.set_text("")
    if ( clave1st == clave2nd ):
      self.doMountNewCargo(clave1st)
    else:
      logging.debug("Passwords do not match")
      self.messageArea.addError(_("Passwords do not match mounted aborted"))
    
    

  def passwordEntry_activate_cb(self, widget, data=None):
    clave=self.passwdDialogText.get_text()
    self.passwdDialogMount.hide()        
    self.passwdDialogText.set_text("")    
    self.doMountNewCargo(clave)
    
  def addNew_clicked_cb(self, widget, data=None):
    logging.debug("Name [%s] SCD[%s] MPD[%s]", self.newName.get_text(), self.newSecretCargoDir.get_filename(), self.newMountPointDir.get_filename())
    self.newCargoWindow.hide()
    self.model.append([_("notChecked"), self.newName.get_text() , self.newSecretCargoDir.get_filename(), self.newMountPointDir.get_filename(), encfsgui.ICON_CHECKING_PENDING])
    self.saveConfig()
    self.checkCargoState()
    self.messageArea.addOK(_("New cargo created! {}").format(self.newName.get_text()))

  def confirmEdit_clicked_cb(self, widget, data=None):
    logging.debug("Name [%s] SCD[%s] MPD[%s]", self.editName.get_text(), self.editSecretCargoDir.get_filename(), self.editMountPointDir.get_filename())
    self.editCargoWindow.hide()
    self.doDelete()
    self.model.append([_("notChecked"), self.editName.get_text() , self.editSecretCargoDir.get_filename(), self.editMountPointDir.get_filename(), encfsgui.ICON_CHECKING_PENDING])
    self.saveConfig()
    self.messageArea.addOK(_("Edit cargo done! {}").format(self.editName.get_text()))

    
  def cancelEdit_clicked_cb(self, widget, data=None):
    logging.debug("cancelEditPressed")
    self.editCargoWindow.hide()  
    self.messageArea.addOK(_("Edit Cargo canceled"))
    
  def cancelNew_clicked_cb(self, widget, data=None):
    logging.debug("cancelNewPressed")
    self.newCargoWindow.hide()    
    self.messageArea.addOK(_("Cargo Creation canceled"))

  def deleteCancel_clicked_cb(self, widget, data=None):
    logging.debug("canceledPressed")
    self.deleteCargoDialog.hide()
    self.messageArea.addOK(_("Delete Cargo canceled"))    

  def deleteConfirm_clicked_cb(self, widget, data=None):
    logging.debug("deletePressed")
    self.deleteCargoDialog.hide()
    self.doDelete()    
    logging.debug("delete cliked!")
    self.messageArea.addOK(_("Delete Cargo confirmed"))    

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
    with open(self.cargoFile, "w") as yamlFile:
      dictFile = dict()      
      for row in self.model:
        dictRow = dict()
        dictRow["secret"] = row[2]
        dictRow["clear"] = row[3]
        dictFile[row[1]] = dictRow
      yaml.dump(dictFile, yamlFile)
      
  def loadConfig(self):
    with open(self.cargoFile, "r") as yamlFile:
      cfg = yaml.load(yamlFile, Loader=yaml.FullLoader)
      for key, value in cfg.items():
        self.model.append([_("notChecked"), key, value["secret"], value["clear"], encfsgui.ICON_CHECKING_PENDING ])
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
        row[0] = _("mounted")
        row[4] = encfsgui.ICON_MOUNTED
        self.activeMount[row[1]] = "on"
        self.readyCargos[row[1]] = "ready"
      else:
        logging.debug("%s NOT mounted", row[3])
        if self.checkCargoIsReady(os.path.realpath(row[2])):
          row[0] = _("notReady")
          row[4] = encfsgui.ICON_NOT_READY
          if self.readyCargos.has_key(row[1]):
            self.readyCargos.pop(row[1])
          if self.activeMount.has_key(row[1]):
            self.activeMount.pop(row[1])                      
        else:
          row[0] = _("unmounted")
          row[4] = encfsgui.ICON_NOT_MOUNTED
          self.readyCargos[row[1]] = "ready"
          if self.activeMount.has_key(row[1]):
            self.activeMount.pop(row[1])

  def __init__(self, cargoFile, configDir):
    self.cargoFile =os.path.realpath(cargoFile)
    gladeFile = configDir+encfsgui.GLADEFILENAME;
    
    self.activeMount = dict()
    self.readyCargos = dict()
    builder = Gtk.Builder()
    builder.set_translation_domain("messages")
    builder.add_from_file(gladeFile)


    builder.connect_signals(self)
    
    self.activateButtons(builder)
    self.cargoList = builder.get_object("cargoList")
    
    renderer_pixbuf = Gtk.CellRendererPixbuf()
    column_pixbuf = Gtk.TreeViewColumn(_("status"), renderer_pixbuf, icon_name=4)
    self.cargoList.remove_column(self.cargoList.get_column(4))
    self.cargoList.append_column(column_pixbuf)
    
    self.cargoList.set_visible(True)    
    self.model = self.cargoList.get_model()
    self.window = builder.get_object("window")
    self.passwdDialogMount = builder.get_object("passwordDialogMount")
    self.passwdDialogText = builder.get_object("passwordEntry")    
    self.passwdDialogNewCargo= builder.get_object("passwordDialogNewCargo")    
    self.passwordEntryNewCargoFirst = builder.get_object("passwordEntryNewCargoFirst")
    self.passwordEntryNewCargoSecond= builder.get_object("passwordEntryNewCargoSecond")    
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
    self.messageArea = messageArea(builder)

    self.loadConfig()
    self.window.show_all()
    self.messageArea.addOK(_("Launched"))
    

if __name__ == "__main__":
  '''Command line options.'''

  program_name = os.path.basename(sys.argv[0])
  program_version = "v%s" % __version__
  program_build_date = str(__updated__)
  program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
  program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
  program_license = '''%s
  
  Created by Andrés Cancer on %s.
  Copyright 2020 Personal. All rights reserved.
  
  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

  USAGE
  ''' % (program_shortdesc, str(__date__))
  defaultCargoFile="{}/.config/encfsgui/{}".format(expanduser("~"),"encfsgui.yaml")
  defaultConfigDir="/usr/share/encfsgui"

   
  # Setup argument parser
  parser = ArgumentParser(description=program_license,
                            formatter_class=RawDescriptionHelpFormatter,
                            epilog=program_version_message)
  parser.add_argument("-d",
                        "--debug",
                        default=False,
                        dest="debug",
                        action="store_true", 
                        help="Activate Debug [default: %(default)s]")
                              
  parser.add_argument("-c",
                        "--cargoFile",
                        default=defaultCargoFile,
                        dest="cargoFile",
                        action="store", 
                        help="location of the file that contains the cargos to be managed [default: %(default)s]")
  parser.add_argument("-g",
                          "--configDir",
                          default=defaultConfigDir,
                          dest="configDir", 
                          action="store",
                          help="location of the app configuration directory [default: %(default)s]")
  
  # Process arguments
  args = parser.parse_args()
  cargoFile = args.cargoFile
  configDir = args.configDir
  dirLocale = configDir+"/locales"
  import locale
  locale.setlocale(locale.LC_ALL)
  locale.bindtextdomain("messages", dirLocale)
  
  try:
    myLang = gettext.translation('messages', localedir=dirLocale)#, languages=['es_ES.utf8'])
    myLang.install()
    _=myLang.gettext
  except:
    myLang = gettext.translation('messages', localedir=dirLocale, languages=['en'])
    myLang.install()
    _=myLang.gettext    
  
  
  debug = args.debug  
  FORMAT = '%(asctime)-15s -12s %(levelname)-8s %(message)s'
  formatter = logging.Formatter(FORMAT)
  
  handler = logging.StreamHandler()
  handler.setFormatter(formatter)
  
  logger = logging.getLogger()  
  logger.addHandler(handler)
  logger.setLevel(logging.CRITICAL)
  if ( debug ):
    logger.setLevel(logging.DEBUG)  

  app = encfsgui(cargoFile,configDir)
  Gtk.main()
