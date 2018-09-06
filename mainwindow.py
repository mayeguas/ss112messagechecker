from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QRadioButton, QComboBox, QPlainTextEdit)

from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QThread

from PyQt5.QtGui import QIcon

from xmlrpcserver import Server

from adaptor import Adaptor, Message, Attribute, CHECK_FOR_ATTRIBUTE_ASSIGN_AND_RETURN_ERRORSTRING_IF_NOT_DEFINED_OR_NOT_CONTAINS

from datetime import datetime

import os

import sys

import xml.etree.ElementTree as ET

import xmlrpc.client

from xmlrpclient import MyTransport

from logwindow import ServerLog, ClientLog

class MainWindow(QWidget):
	
	def __init__(self):
		""" Constructor for QWidget and mainWindow """
		super().__init__()
		self.data = {}
		self.initUI()
		
		sLoadResult = self.loadConfigData()
		if (sLoadResult == ""): 
			self.printMessageToLog("Configuration file load succesfully")
		else:
			self.printMessageToLog(sLoadResult)
		
	def initUI(self):
		
		self.setGeometry(300, 300, 800, 600)
		self.setWindowTitle('SS111_2 Message Checker')
		self.setWindowIcon(QIcon("icon.ico"))
		
		"""
		#########################
		###		 LAYOUT       ###
		#########################
		"""
		
		self.vLayout = QVBoxLayout()
		
		self.hTopLayout = QHBoxLayout()
		self.vTopLeftLayout = QVBoxLayout()
		self.vTopRightLayout = QVBoxLayout()
		
		self.hMidLayout = QHBoxLayout()
		self.vMidRightLayout = QVBoxLayout()
		
		self.hBotLayout = QHBoxLayout()
		self.vBotLeftLayout = QVBoxLayout()
		self.vBotRightLayout = QVBoxLayout()
		
		"""
		#########################
		###		 WIDGETS       ###
		#########################
		"""
		
		self.modeSelectionLabel = QLabel("Select a Configuration Mode")
		self.modeSelectionLabel.setStyleSheet(""" .QLabel { 
												font-family: Helvetica; 
												font-size: 15px;
												text-decoration: underline;
												}""")
		
		self.OBUButton = QRadioButton('OBU-ADAPTOR MODE', self)
		self.TCLButton = QRadioButton('TCL MODE', self)
		
		self.setStyleSheet(""" QRadioButton:checked { 
															color: #ea472e; 
															font-weight: bold;
															
															}""")
		
		self.OBUButton.clicked.connect(self.setOBUMode)
		self.TCLButton.clicked.connect(self.setTCLMode)
		
		self.communicationLabel = QLabel("Network State")
		self.communicationLabel.setStyleSheet(""" .QLabel { 
												font-family: Helvetica; 
												font-size: 15px;
												text-decoration: underline;
												}""")
		self.serverLabel = QLabel("Server listening at: ")
		self.clientLabel = QLabel("Client connecting with: ")	
		
		self.modeLabel = QLabel(self)
		self.modeLabel.setStyleSheet(""" .QLabel { 
												font-family: Helvetica; 
												font-size: 20px;
												border-top: 1px solid black;
												border-bottom: 1px solid black;
												qproperty-alignment: AlignCenter;
												}""")
		self.modeLabel.hide()
		
		self.messageTableWidget = QTableWidget(self)
		self.messageTableWidget.cellClicked.connect(self.messageSelected)
		self.messageTableWidget.hide()
		
		self.messageTableWidget.setStyleSheet(""" QTableWidget:item:selected { background-color: #758091; color: white; font: bold 12px; } .QHeaderView::section {  background-color: #dedfe0; color: black; font: bold 12px;}  .QHeaderView::section:checked { font: bold 12px;}""")
		
		self.currentMessageTableWidget = QTableWidget(self)
		self.currentMessageTableWidget.setStyleSheet(""" .QHeaderView::section { background-color: #dedfe0; color: black; font: bold 12px; }  .QHeaderView::section:checked {font: bold 12px;} QTableWidget:item:selected { background-color: #758091; color: white; font: bold 12px; }""")
		self.currentMessageTableWidget.hide()
		
		self.sendButton = QPushButton("Send", self)
		self.sendButton.setStyleSheet(""" .QPushButton { background-color: #c3c5c9; color: black; font: bold 14px; border-style: outset; border-width: 2px; border-radius: 10px; border-color: black; } 
		.QPushButton:pressed { background-color: #758091; color: white; border-color: white} """)
		self.sendButton.hide()
		
		self.sendButton.clicked.connect(self.sendMessage)
		
		clientLogFileName = "../logs/client%s.log" % (datetime.now().strftime("%Y%m%d%H%M%S"))
		ClientLog.pClientLogFile = clientLogFileName
		
		logDirectory = '../logs'
		if not os.path.exists(logDirectory):
			os.makedirs(logDirectory)
			
		with open (ClientLog.pClientLogFile, 'w'):
				pass
		
		clientLogTextEdit = QPlainTextEdit(self)
		clientLogTextEdit.setReadOnly(True)
		ClientLog.pPlainTextEdit = clientLogTextEdit
		self.clientLogTitle = QLabel("Client Log File")
		self.clientLogTitle.setStyleSheet(""" .QLabel { 
												font-family: Helvetica; 
												font-size: 15px;
												text-decoration: underline;
												}""")
		
		
		serverLogFileName = "../logs/server%s.log" % (datetime.now().strftime("%Y%m%d%H%M%S"))
		ServerLog.pServerLogFile = serverLogFileName
		with open (ServerLog.pServerLogFile, 'w'):
			pass
		
		#self.serverLogTextEdit = LogWidget(serverLogFileName, self)
		serverLogTextEdit = QPlainTextEdit(self)
		serverLogTextEdit.setReadOnly(True)
		ServerLog.pPlainTextEdit = serverLogTextEdit
		self.serverLogTitle = QLabel("Server Log File")
		self.serverLogTitle.setStyleSheet(""" .QLabel { 
												font-family: Helvetica; 
												font-size: 15px;
												text-decoration: underline;
												}""")
		
		"""
		#########################
		###		 DESIGN       ###
		#########################
		"""
		
		self.vTopLeftLayout.addWidget(self.modeSelectionLabel)
		self.vTopLeftLayout.addWidget(self.OBUButton)
		self.vTopLeftLayout.addWidget(self.TCLButton)
		
		self.vTopRightLayout.addWidget(self.communicationLabel)
		self.vTopRightLayout.addWidget(self.serverLabel)
		self.vTopRightLayout.addWidget(self.clientLabel)
		
		self.hTopLayout.addLayout(self.vTopLeftLayout)
		self.hTopLayout.addLayout(self.vTopRightLayout)
		
		self.vLayout.addLayout(self.hTopLayout)
		
		self.vLayout.addWidget(self.modeLabel)
		
		self.hMidLayout.addWidget(self.messageTableWidget, 1)
		
		self.vMidRightLayout.addWidget(self.currentMessageTableWidget)
		self.vMidRightLayout.addWidget(self.sendButton)
		
		self.hMidLayout.addLayout(self.vMidRightLayout, 3)
		
		self.vLayout.addLayout(self.hMidLayout)
	
		self.vBotLeftLayout.addWidget(self.clientLogTitle)
		self.vBotLeftLayout.addWidget(clientLogTextEdit)
		
		self.vBotRightLayout.addWidget(self.serverLogTitle)
		self.vBotRightLayout.addWidget(serverLogTextEdit)
		
		self.hBotLayout.addLayout(self.vBotLeftLayout)
		self.hBotLayout.addLayout(self.vBotRightLayout)
		
		self.vLayout.addLayout(self.hBotLayout)
				
		self.setLayout(self.vLayout)

	def loadConfigData(self):
		
		""" Load the configuration file and create the adaptor with the given parameters """
		
		configFileName = "../config/base_TCL_config.xml"
		
		try:
			configData_tree = ET.parse(configFileName)
		except FileNotFoundError:
			error = "Error:<br>Configuration file: '%s' not found<br>Exiting program" % (configFileName)
			showErrorMessageBox(error)
			sys.exit()
		
		configData_root = configData_tree.getroot()
		
		if (configData_root.tag != 'tcl'):
			return "Error loading configuration file: Expecting <tcl> but <%s> found." % (configData_root.tag)
		
		adaptor_tag = configData_root.find('adaptor')
		
		if (adaptor_tag == None):
			return "Expecting <adaptor> but not found."
		
		else:
			name, listenPort, listenAddress, remoteURL, adaptorDefinitionFile = [], [], [], [], []
			CHECK_FOR_ATTRIBUTE_ASSIGN_AND_RETURN_ERRORSTRING_IF_NOT_DEFINED_OR_NOT_CONTAINS(name, adaptor_tag, 'name')
			CHECK_FOR_ATTRIBUTE_ASSIGN_AND_RETURN_ERRORSTRING_IF_NOT_DEFINED_OR_NOT_CONTAINS(listenPort, adaptor_tag, 'listenPort')
			CHECK_FOR_ATTRIBUTE_ASSIGN_AND_RETURN_ERRORSTRING_IF_NOT_DEFINED_OR_NOT_CONTAINS(listenAddress, adaptor_tag, 'listenAddress')
			CHECK_FOR_ATTRIBUTE_ASSIGN_AND_RETURN_ERRORSTRING_IF_NOT_DEFINED_OR_NOT_CONTAINS(remoteURL, adaptor_tag, 'remoteURL')
			CHECK_FOR_ATTRIBUTE_ASSIGN_AND_RETURN_ERRORSTRING_IF_NOT_DEFINED_OR_NOT_CONTAINS(adaptorDefinitionFile, adaptor_tag, 'adaptorDefinitionFile')
			
			try:
				self.adaptor = Adaptor(name[0], listenPort[0], listenAddress[0], remoteURL[0], adaptorDefinitionFile[0])
			except FileNotFoundError:
				error = "Error:<br>Adaptor definition file: '%s' not found<br>Exiting program" % (adaptorDefinitionFile[0])
				showErrorMessageBox(error)
				sys.exit()
			else:
				if(self.adaptor.error != ""):
					showErrorMessageBox(self.adaptor.error)
					sys.exit()
			
		return ""
			
	def setOBUMode(self):
		
		""" OBU ADAPTOR MODE selected from MainWindow """
		
		self.mode = "OBU ADAPTOR"
		
		self.modeLabel.show()
		self.modeLabel.setText(self.OBUButton.text())
		
		# Set table with toTCL Messages
		
		self.messageTableWidget.clear()
		
		OBUtableWidget = self.messageTableWidget
		
		OBUtableWidget.clear()
		
		OBUtableWidget.setRowCount(0)
		
		self.currentMessageTableWidget.hide()
		self.sendButton.hide()
		
		tableHeadersList = ["Message to TCL"]
		
		OBUtableWidget.setColumnCount(len(tableHeadersList))
		OBUtableWidget.setHorizontalHeaderLabels(tableHeadersList)
		OBUtableWidget.horizontalHeader().setStretchLastSection(True)
		OBUtableWidget.verticalHeader().hide()
		
		for message in self.adaptor.messageList:
			if (message.direction == "toTCL"):
				tableWidgetItem = QTableWidgetItem(message.name)
				OBUtableWidget.setRowCount(OBUtableWidget.rowCount() + 1)
				OBUtableWidget.setItem(OBUtableWidget.rowCount() - 1, 0, tableWidgetItem)
			
		self.messageTableWidget.show()
		
		# Create OBU ADAPTOR Server
		
		self.createServer(str(self.adaptor.listenIp), int(self.adaptor.listenPort))
		
	def setTCLMode(self):
		
		""" TCL MODE selected from MainWindow """
		
		self.mode = "TCL"
		
		self.modeLabel.show()
		self.modeLabel.setText(self.TCLButton.text())
		
		self.messageTableWidget.clear()
		
		TCLtableWidget = self.messageTableWidget
		
		TCLtableWidget.clear()
		
		TCLtableWidget.setRowCount(0)
		
		self.currentMessageTableWidget.hide()
		self.sendButton.hide()
		
		tableHeadersList = ["Message to OBU"]
		
		TCLtableWidget.setColumnCount(len(tableHeadersList))
		TCLtableWidget.setHorizontalHeaderLabels(tableHeadersList)
		TCLtableWidget.horizontalHeader().setStretchLastSection(True)
		TCLtableWidget.verticalHeader().hide()
		
		for message in self.adaptor.messageList:
			if (message.direction == "toAdaptor"):
				tableWidgetItem = QTableWidgetItem(message.name)
				TCLtableWidget.setRowCount(TCLtableWidget.rowCount() + 1)
				TCLtableWidget.setItem(TCLtableWidget.rowCount() - 1, 0, tableWidgetItem)
			
		self.messageTableWidget.show()
		
		# Create TCL Server
				
		self.createServer(str(self.adaptor.listenIp), int(self.adaptor.listenPort))
		
	def createServer(self, serverIp, serverPort):
		
		self.clientLabel.setText("<b>%s</b> Client connecting with <b>%s</b>" % (self.mode, self.adaptor.remoteUrl))
		ClientLog.appendMessage(ClientLog.pPlainTextEdit, ClientLog.pClientLogFile, "%s Client connecting with %s" % (self.mode, self.adaptor.remoteUrl))
		
		try:
			if (self.serverThread.isRunning()):
				self.serverThread.quit()
		except AttributeError:
			pass
		
		try:
			self.serverThread = Connection(str(serverIp), int(serverPort), self.adaptor)
		except OSError as err:
			error = "Error:<br>Is not possible to bind the server to the address <b>%s:%i</b><br>Change configuration file" % (str(serverIp), int(serverPort))
			showErrorMessageBox(error)
			sys.exit()
		else:
			self.serverLabel.setText("<b>%s</b> Server listening at <b>%s:%i</b>" % (self.mode, serverIp, serverPort))
			ServerLog.appendMessage(ServerLog.pPlainTextEdit, ServerLog.pServerLogFile, "%s Server listening at %s:%i" % (self.mode, serverIp, serverPort))
			
			self.serverThread.start()
			
	def messageSelected(self, row, column):
		
		messageName = self.messageTableWidget.item(row, column).text()
		
		for message in self.adaptor.messageList:
			if message.name == messageName:
				self.currentMessage = Message(message.name, message.direction, message.variableList)
		
		self.currentMessageTableWidget.clear()
		
		if (len(self.currentMessage.variableList) != 0):
			
			currenMessageTableHeadersList = ["Variable", "Type", "Value", "Description"]
			
		else:
			
			currenMessageTableHeadersList = ["No Variables"]
		
		self.currentMessageTableWidget.setColumnCount(len(currenMessageTableHeadersList))
		self.currentMessageTableWidget.setHorizontalHeaderLabels(currenMessageTableHeadersList)
		self.currentMessageTableWidget.horizontalHeader().setStretchLastSection(True)
		self.currentMessageTableWidget.verticalHeader().hide()
		self.currentMessageTableWidget.setRowCount(len(self.currentMessage.variableList))
		
		for i, variable in enumerate(self.currentMessage.variableList):
			
			tableWidgetItem = QTableWidgetItem(variable.name)
			tableWidgetItem.setFlags(Qt.ItemIsEnabled)
			self.currentMessageTableWidget.setItem(i, 0, tableWidgetItem)
			
			tableWidgetItem = QTableWidgetItem(variable.type)
			tableWidgetItem.setFlags(Qt.ItemIsEnabled)
			self.currentMessageTableWidget.setItem(i, 1, tableWidgetItem)
			
			if (variable.type == "boolean"):
				
				comboBoxBool = QComboBox()
				comboBoxBool.insertItem(0, "true")
				comboBoxBool.insertItem(1, "false")
				self.currentMessageTableWidget.setCellWidget(i, 2, comboBoxBool)
				
			else:
								
				if (variable.name == "timeStamp"):
					valueText = datetime.now().strftime("%Y-%m-%d-%H:%M:%S.%f")[:-3]
				
				else:
					valueText = str(variable.defaultValue)
					
				tableWidgetItem = QTableWidgetItem(valueText)
				tableWidgetItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
				self.currentMessageTableWidget.setItem(i, 2, tableWidgetItem)
				
			
			tableWidgetItem = QTableWidgetItem(variable.description)
			tableWidgetItem.setFlags(Qt.ItemIsEnabled)
			self.currentMessageTableWidget.setItem(i, 3, tableWidgetItem)
			
		self.currentMessageTableWidget.setVisible(False)
		self.currentMessageTableWidget.resizeColumnsToContents()
		self.currentMessageTableWidget.resizeRowsToContents()
		self.currentMessageTableWidget.setVisible(True)
		
		self.currentMessageTableWidget.show()
		self.sendButton.show()
			
	def sendMessage(self):
		
		if (self.currentMessage.name == ''):
			showErrorMessageBox("Error: No message Selected")
			return
		
		vars = {}
		
		for i, variable in enumerate(self.currentMessage.variableList):
		
			cellWidget = self.currentMessageTableWidget.cellWidget(i, 2)
			if (cellWidget):
				if (cellWidget.metaObject().className() == "QComboBox"):
					value = cellWidget.currentText()
			else:			
				
				widgetItem = QTableWidgetItem(self.currentMessageTableWidget.item(i, 2))
				value = widgetItem.text()
			 
			if (value == ''):
			 	
			 	showErrorMessageBox("Error: '%s' with empty value" % (variable.name))
			 	return
			
			vars[variable.name] = variable.checkValue(value)
			
			if (str(vars[variable.name])[:5] == 'Error'):
				showErrorMessageBox(vars[variable.name])
				return

		proxy = xmlrpc.client.ServerProxy(self.adaptor.remoteUrl, transport=MyTransport())
			
		try:
			getattr(proxy, self.currentMessage.name)(vars)
		except ConnectionError as err:
			error = "Client error:<br>Is not possible to stablish connection with the server <b>%s</b>" % (self.adaptor.remoteUrl)
			ClientLog.appendMessage(ClientLog.pPlainTextEdit, ClientLog.pClientLogFile, error)
			showErrorMessageBox(error)
		except xmlrpc.client.Fault as err:
			error = "Server <b>%s</b> error:<br>Fault code: %d | Fault string: %s" % (self.adaptor.remoteUrl, err.faultCode, err.faultString)
			ClientLog.appendMessage(ClientLog.pPlainTextEdit, ClientLog.pClientLogFile, error)
			showErrorMessageBox(error)
		
	def printMessageToLog(self, text):
		
		ClientLog.appendMessage(ClientLog.pPlainTextEdit, ClientLog.pClientLogFile, text)
		ServerLog.appendMessage(ServerLog.pPlainTextEdit, ServerLog.pServerLogFile, text)
		
	def closeEvent(self, event):

		try:
			if (self.serverThread.isRunning()):
				self.serverThread.quit()
		except AttributeError:
			pass
class Connection(QThread):
	
	def __init__(self, serverIp, serverPort, adaptor):
		
		super().__init__()
		
		self.OK = True
		
		self.server = Server((serverIp, serverPort), adaptor)

		self.server.register_introspection_functions()
		
		self.server.dataReceived.connect(self.on_dataReceived)
		self.server.dataSend.connect(self.on_dataSend)
		self.server.dataBadFormed.connect(self.on_dataBadFormed)

	def run(self):
		while (self.OK):
			self.server.serve_forever()
	
	def close(self):
		self.OK = False
		self.server.shutdown()	
	
	def on_dataReceived(self, data):
		ServerLog.appendMessage(ServerLog.pPlainTextEdit, ServerLog.pServerLogFile, "Received:\n%s" % (data))
		
	def on_dataSend(self, data):
		ServerLog.appendMessage(ServerLog.pPlainTextEdit, ServerLog.pServerLogFile, "Send:\n%s" % (data))
		
	def on_dataBadFormed(self, data):
		showErrorMessageBox(data)
		
def showErrorMessageBox(errorString):
	
	msgBox = QMessageBox()
	msgBox.setWindowTitle("ERROR")
	msgBox.setText(errorString)
	msgBox.setIcon(QMessageBox.Critical)
	msgBox.exec()
	