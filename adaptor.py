import base64
import re
import xml.etree.ElementTree as ET
from logwindow import ServerLog, ClientLog
import sys

def CHECK_FOR_ATTRIBUTE_ASSIGN_AND_RETURN_ERRORSTRING_IF_NOT_DEFINED_OR_NOT_CONTAINS(STRINGASSIGN, ELEMENT, STRINGATTRIBUTENAME):
	STRINGASSIGN.append(ELEMENT.get(STRINGATTRIBUTENAME))
	if (STRINGASSIGN[0] == None):
		return "Attribute %s must be defined and not empty for the <%s> element" % (STRINGATTRIBUTENAME, ELEMENT.tag)

class Attribute():
    
	def __init__(self, name, type, description, defaultValue):
        
		self.name = name
		self.type = type
		self.description = description
		self.defaultValue = defaultValue
        
	def checkValue(self, value):
        
		if (self.type == "string"):
			value_ = str(value)
                         
		elif (self.type == "int"):
			try:
				value_ = int(value)
			except ValueError:
				return "Error in variable '%s' converting value '%s' to %s type" % (self.name, value, self.type)
                         
		elif (self.type == "boolean"):
			if (value == "true"):
				value_ = True
			elif(value == "false"):
				value_ = False
                             
		elif (self.type == "double"):
			try:
				value_ = float(value)
			except ValueError:
				return "Error in variable '%s' converting value '%s' to %s type" % (self.name, value, self.type)

		elif (self.type == "base64"):
			try:
				value_ = base64.b64encode(value.encode())
			except TypeError:
				return "Error in variable '%s' converting value '%s' to %s type" % (self.name, value, self.type)
                         
		elif (self.type == "array(string)"):
			try:
				if (value[0] != '['):
					return "Error in variable '%s'('%s' type): '%s' must start with square brackets" % (self.name, self.type, value)
				elif(value[-1] != ']'):
					return "Error in variable '%s'('%s' type): '%s' must end with square brackets" % (self.name, self.type, value)
				else:
					value_ = []
					for string in value[1:-1].split(','):
						value_.append(str(string))
						if (value_ == ['']):
							return "Error in variable '%s': '%s' is not a comma separated list" % (self.name, value[1:-1])
                         
			except IndexError:
				return "Error in variable '%s'(%s type): Cannot access to index 1 or -1 in '%s' value" % (self.name, self.type, value)                         
				
		elif (self.type == "array(array(string))"):
			try:
				if (value[0] != '['):
					return "Error in variable '%s'('%s' type): '%s' must start with square brackets" % (self.name, self.type, value)
				elif(value[-1] != ']'):
					return "Error in variable '%s'('%s' type): '%s' must end with square brackets" % (self.name, self.type, value)
				elif (value[1] != '[' or value[-2] != ']'):
					return "Error in variable '%s'('%s' type): '%s' must be encapsulated in square brackets" % (self.name, self.type, value[1:-1])
			except IndexError:
				return "Error in variable '%s'(%s type): Cannot check '%s' value" % (self.name, self.type, value)
			else:
				list = []
				index = 1
				while (index < len(value[1:-1]) - 2):
					m = re.search(r'\[(\w+,?)+\]', value[index:-1])
					if (m == None):
						break
					index += m.group().find(']')    
                         
					list.append(m.group())
				value_ = []
                         
				for array in list:
					sublist = []
					for string in array[1:-1].split(','):
						sublist.append(str(string))
					value_.append(sublist)
                         
				if (value_ == []):
					return "Error in variable '%s': '%s' is not a comma separated list" % (self.name, value[1:-1])
                         
		elif (self.type == "array(int)"):
			try:
				if (value[0] != '['):
					return "Error in variable '%s'('%s' type): '%s' must start with square brackets" % (self.name, self.type, value)
				elif(value[-1] != ']'):
					return "Error in variable '%s'('%s' type): '%s' must end with square brackets" % (self.name, self.type, value)
			except IndexError:
				return "Error in variable '%s'(%s type): Cannot check '%s' value" % (self.name, self.type, value)
			else:
				try:
					value_ = []
					for string in value[1:-1].split(','):
						value_.append(int(string))
					if (value_ == ['']):
						return "Error in variable '%s': '%s' is not a comma separated list" % (self.name, value[1:-1])
				except ValueError:
					return "Error in variable '%s': is not posible to convert '%s' to int" % (self.name, string)
                         
		elif (self.type == "array(double)"):
			try:
				if (value[0] != '['):
					return "Error in variable '%s'('%s' type): '%s' must start with square brackets" % (self.name, self.type, value)
				elif(value[-1] != ']'):
					return "Error in variable '%s'('%s' type): '%s' must end with square brackets" % (self.name, self.type, value)
			except IndexError:
				return "Error in variable '%s'(%s type): Cannot check '%s' value" % (self.name, self.type, value)
			else:
				try:
					value_ = []
					for string in value[1:-1].split(','):
						value_.append(float(string))
					if (value_ == ['']):
						return "Error in variable '%s': '%s' is not a comma separated list" % (self.name, value[1:-1])
				except ValueError:
					return "Error in variable '%s': is not posible to convert '%s' to double" % (self.name, string)
                         
		return value_

class Message():
    
    def __init__(self, name, direction, variableList):
        
        self.name = name
        self.direction = direction
        self.variableList = variableList
        
        self.variableNameList = []
        
        for variable in variableList:
            self.variableNameList.append(variable.name)

class Adaptor():

    def __init__(self, name, listenPort, listenIp, remoteUrl, adaptorDefinitionFile):
    
        self.name = name
        self.listenPort = listenPort
        self.listenIp = listenIp
        self.remoteUrl = remoteUrl
        self.adaptorDefinitionFile = adaptorDefinitionFile
        self.error = ''
        self.messageList = []
        self.messageDict = {}
        self.messageNameList = []
        sLoadResult = self.loadDefinitionFile(self.adaptorDefinitionFile)
        if (sLoadResult == ''):
        	ClientLog.appendMessage(ClientLog.pPlainTextEdit, ClientLog.pClientLogFile, "Adaptor Definition file load succesfully")
        	ServerLog.appendMessage(ServerLog.pPlainTextEdit, ServerLog.pServerLogFile, "Adaptor Definition file load succesfully")
        else:
        	ClientLog.appendMessage(ClientLog.pPlainTextEdit, ClientLog.pClientLogFile, sLoadResult)
        	ServerLog.appendMessage(ServerLog.pPlainTextEdit, ServerLog.pServerLogFile, sLoadResult)
        	self.error = "Error when creating adaptor %s\n%s" % (self.name, sLoadResult)
        
    
    def loadDefinitionFile(self, adaptorDefinitionFile):
        
        try:
            adaptor_tree = ET.parse(adaptorDefinitionFile)
        except ET.ParseError as err:
            return "Error when parsing %s file:\n%s" % (adaptorDefinitionFile, err.args[0])
        
        adaptor_root = adaptor_tree.getroot()
        
        if (adaptor_root.tag != 'adaptor'):
            return "Error loading adaptor definition file: Expecting <adaptor> but <%s> found." % (adaptor_root.tag)
        
        message_tag = adaptor_root.findall('message')
        
        if (message_tag == []):
             return "Expecting <message> but not found."
        else:     
            for message in message_tag:
                
                message_name, message_direction = [], []
                CHECK_FOR_ATTRIBUTE_ASSIGN_AND_RETURN_ERRORSTRING_IF_NOT_DEFINED_OR_NOT_CONTAINS(message_name, message, 'name')
                CHECK_FOR_ATTRIBUTE_ASSIGN_AND_RETURN_ERRORSTRING_IF_NOT_DEFINED_OR_NOT_CONTAINS(message_direction, message, 'direction')
                
                message_variableList = []                   
                
                for variable_tag in message.findall('variable'):
                    
                    attribute_name, attribute_type, attribute_description, attribute_defaultValue = [], [], [], []
                    CHECK_FOR_ATTRIBUTE_ASSIGN_AND_RETURN_ERRORSTRING_IF_NOT_DEFINED_OR_NOT_CONTAINS(attribute_name, variable_tag, 'name')
                    CHECK_FOR_ATTRIBUTE_ASSIGN_AND_RETURN_ERRORSTRING_IF_NOT_DEFINED_OR_NOT_CONTAINS(attribute_type, variable_tag, 'type')
                    CHECK_FOR_ATTRIBUTE_ASSIGN_AND_RETURN_ERRORSTRING_IF_NOT_DEFINED_OR_NOT_CONTAINS(attribute_description, variable_tag, 'description')
                    CHECK_FOR_ATTRIBUTE_ASSIGN_AND_RETURN_ERRORSTRING_IF_NOT_DEFINED_OR_NOT_CONTAINS(attribute_defaultValue, variable_tag, 'defaultValue')
                    
                    attribute = Attribute(attribute_name[0], attribute_type[0], attribute_description[0], attribute_defaultValue[0])
                    
                    message_variableList.append(attribute)
            
                message = Message(message_name[0], message_direction[0], message_variableList)
                
                self.messageList.append(message)
                self.messageNameList.append(message.name)
                self.messageDict[message.name] = message
                
        return ""
        
           
