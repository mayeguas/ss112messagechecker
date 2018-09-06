import xml.etree.ElementTree as ET
import base64

adaptorDefinitionFile="Subset-111-2_IOP_FFFIS_OBU-v360_message-definitions.xml"

adaptor_tree = ET.parse(adaptorDefinitionFile)
adaptor_root = adaptor_tree.getroot()
        
for message_tag in adaptor_root.iter('message'):
            
	for variable_tag in message_tag.iter('variable'):
        
		if (variable_tag.get('type') == "string"):
			variable_tag.set('defaultValue', variable_tag.get('name'))
		elif (variable_tag.get('type') == "int"):
			variable_tag.set('defaultValue', "1")
		elif (variable_tag.get('type') == "double"):
			variable_tag.set('defaultValue', "1.0")
		elif (variable_tag.get('type') == "array(double)"):
			variable_tag.set('defaultValue', "[1.0,1.0]")
		elif (variable_tag.get('type') == "array(int)"):
			variable_tag.set('defaultValue', "[1,1]")
		elif (variable_tag.get('type') == "base64"):
			variable_tag.set('defaultValue', base64.b64encode(variable_tag.get('name')))
		elif (variable_tag.get('type') == "array(string)"):
			variable_tag.set('defaultValue', "[%s]" % (variable_tag.get('name')))
		elif (variable_tag.get('type') == "array(array(string))"):
			variable_tag.set('defaultValue', "[[%s]]" % (variable_tag.get('name')))
		

adaptor_tree.write("Subset-111-2_IOP_FFFIS_OBU-v360_message-definitions_v1.xml")
