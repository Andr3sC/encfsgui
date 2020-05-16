class messageArea(object):
  '''
  This object will handle the message area which shows errors, confirmations and work in progress.
  '''


  def __init__(self, builder):
    '''
    Gets the three areas from builder
    '''
    self.messageAreaOK=builder.get_object("messageAreaOK");
    self.messageAreaInProgress=builder.get_object("messageAreaInProgress");
    self.messageAreaError=builder.get_object("messageAreaError");
    
  def resetMessages(self):
    '''
    Resetes all the messages
    '''
    self.messageAreaError.set_text("")
    self.messageAreaInProgress.set_text("")
    self.messageAreaOK.set_text("")

  def addError(self, message):
    '''
    Resets messages and add an error line
    '''
    self.resetMessages()
    self.messageAreaError.set_text(message)

  def addOK(self, message):
    '''
    Resets messages and add an ok line
    '''    
    self.resetMessages()
    self.messageAreaOK.set_text(message)

  def addInProgress(self, message):
    '''
    Resets messages and add an inProgress line
    '''    
    self.resetMessages()
    self.messageAreaInProgress.set_text(message)
