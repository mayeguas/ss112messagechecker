from adaptor import Adaptor, Message, Attribute

from PyQt5.QtCore import pyqtSignal

from PyQt5.Qt import QWidget

from xmlrpc.server import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer

from xmlrpc.client import dumps, loads

class Server(SimpleXMLRPCServer, QWidget):
	
	dataReceived = pyqtSignal(str)
	dataSend = pyqtSignal(str)
	dataBadFormed = pyqtSignal(str)
	
	def __init__(self, addr, adaptor):
		SimpleXMLRPCServer.__init__(self, addr, requestHandler=SimpleXMLRPCRequestHandler, logRequests=False, allow_none=False, encoding=None, bind_and_activate=True, use_builtin_types=False)
		QWidget.__init__(self)
		self.adaptor = adaptor
		
	def _marshaled_dispatch(self, data, dispatch_method = None, path = None):
		try:
			params, method = loads(data, use_builtin_types=self.use_builtin_types)
			
			self.dataReceived.emit(data.decode())
			
            # generate response
			if dispatch_method is not None:
				response = dispatch_method(method, params)
			else:
				
				response = self._dispatch(method, params)
			# wrap response in a singleton tuple
			response = (response,)
			response = dumps(response, methodresponse=1,
                             allow_none=self.allow_none, encoding=self.encoding)
			
			self.dataSend.emit(response)

		except Fault as fault:
			response = dumps(fault, allow_none=self.allow_none,
                             encoding=self.encoding)
		except:
            # report exception back to server
			exc_type, exc_value, exc_tb = sys.exc_info()
			try:
				response = dumps(
                    Fault(1, "%s:%s" % (exc_type, exc_value)),
                    encoding=self.encoding, allow_none=self.allow_none,
                    )
			finally:
                # Break reference cycle
				exc_type = exc_value = exc_tb = None
				
		return response.encode(self.encoding, 'xmlcharrefreplace')
	
	def _dispatch(self, method, params):
		
		if method in self.adaptor.messageDict.keys():
			
			if ( params == () and len(self.adaptor.messageDict[method].variableNameList) == 0 ):
				return True
			
			else:
				
				if ( type(params[0]).__name__ != 'dict' ):
					return False
				
				elif (set(params[0].keys()) == set(self.adaptor.messageDict[method].variableNameList)):
					
					message = self.adaptor.messageDict[method]
					
					for variable in message.variableList:
						if ( variable.type == "str" ):
							if ( type(params[0][variable.name]).__name__ != 'str' ):
								self.dataBadFormed.emit("Error: %s param received not a %s" % (variable.name, variable.type))
								
						elif ( variable.type == "int" ):
							if ( type(params[0][variable.name]).__name__ != 'int' ):
								self.dataBadFormed.emit("Error: %s param received not a %s" % (variable.name, variable.type))
								
						elif ( variable.type == "boolean" ):
							if ( type(params[0][variable.name]).__name__ != 'bool' ):
								self.dataBadFormed.emit("Error: %s param received not a %s" % (variable.name, variable.type))
						
						elif ( variable.type == "base64" ):
							if ( type(params[0][variable.name]).__name__ != 'Binary' ):
								self.dataBadFormed.emit("Error: %s param received not a %s" % (variable.name, variable.type))
								
						elif ( variable.type == "double" ):
							if ( type(params[0][variable.name]).__name__ != 'float' ):
								self.dataBadFormed.emit("Error: %s param received not a %s" % (variable.name, variable.type))
								
						elif ( variable.type == "array(string)" or variable.type == "array(int)" 
							or variable.type == "array(double)" or variable.type == "array(array(string))" ):
							if ( type(params[0][variable.name]).__name__ != 'list' ):
								self.dataBadFormed.emit("Error: %s param received not a %s" % (variable.name, variable.type))
								
					return True
				else:
					for variable in set(params[0].keys()):
						if variable not in self.adaptor.messageDict[method].variableNameList:
							self.dataBadFormed.emit("Error: '%s' variable received not in %s message" % (variable, method))
							return False
		else:
			self.dataBadFormed.emit("Error: '%s' message received not in adaptor definition file" % (method))
			return False