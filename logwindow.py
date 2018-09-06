from datetime import datetime

class ServerLog:

    def appendMessage(pServerTextEdit, pServerLogFile, text):
        timeNow = datetime.now().strftime("%Y-%m-%d-%H:%M:%S.%f")
        pServerTextEdit.appendPlainText("%s\n" %(timeNow))
        pServerTextEdit.appendPlainText("%s\n" %(text))
        pServerTextEdit.verticalScrollBar().setValue(pServerTextEdit.verticalScrollBar().maximum())
        with open(pServerLogFile, 'a') as f:
            f.write("%s\n" %(timeNow))
            f.write("%s\n" %(text))

class ClientLog:
        
    def appendMessage(pClientTextEdit, pClientLogFile, text):
        timeNow = datetime.now().strftime("%Y-%m-%d-%H:%M:%S.%f")
        pClientTextEdit.appendPlainText("%s\n" %(timeNow))
        pClientTextEdit.appendPlainText("%s\n" %(text))
        pClientTextEdit.verticalScrollBar().setValue(pClientTextEdit.verticalScrollBar().maximum())
        with open(pClientLogFile, 'a') as f:
            f.write("%s\n" %(timeNow))
            f.write("%s\n" %(text))
