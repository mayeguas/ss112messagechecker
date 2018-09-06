from mainwindow import MainWindow

from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
	
	import sys
		
	app = QApplication(sys.argv)
	
	window = MainWindow()
	
	window.showMaximized()
	
	sys.exit(app.exec_())
