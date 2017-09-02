import sys
import os
import Downloader
from PyQt4 import QtCore, QtGui 
from Pl_layout import Ui_MainWindow

class AppGui(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)   
        self.ui.tableWidget.setColumnWidth(0, 200) 
        self.ui.tableWidget.setColumnWidth(1, 90) 
        self.ui.pushButton.clicked.connect(self.pass_inputs_to_downloader)
        QtCore.QCoreApplication.processEvents()

    def pass_inputs_to_downloader(self):
        video_url = self.get_video_url()
        media_type = self.get_media_type()
        download_type = self.get_download_type()
        start_index = self.get_start_index()
        if video_url:
            self.ui.pushButton.setEnabled(False)
            try:
                self.update_status('Starting..')
                Downloader.handle_video_download(video_url, start_index, media_type, download_type, app=self)
            except Exception as e:
                self.show_error_message(e.args)
                self.update_status('Failed!')
            finally:
                self.ui.pushButton.setEnabled(True)
 
    def get_video_url(self):
        video_url = self.ui.lineEdit.text()
        return str(video_url)

    def get_media_type(self):
        media_type_video_button = self.ui.radioButton
        media_type_audio_button = self.ui.radioButton_2
        if media_type_video_button.isChecked():
            media_type = 'video'
        else:
            media_type = 'audio'
        return str(media_type)

    def get_download_type(self):
        download_type_playlist_button = self.ui.radioButton_5
        download_type_single_video_button = self.ui.radioButton_6
        if download_type_playlist_button.isChecked():
            download_type = 'playlist'
        else:
            download_type = 'single'
        return str(download_type)

    def get_start_index(self):
        start_index_playlist_button = self.ui.radioButton_3
        start_index_current_button = self.ui.radioButton_4
        if start_index_playlist_button.isChecked():
            start_index = 'origin'
        else:
            start_index = 'current'
        return str(start_index)

    def add_table_item(self, file_name, file_size, file_progress):
        rowCount = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(rowCount)
        self.ui.tableWidget.setItem(rowCount, 0, QtGui.QTableWidgetItem(file_name))
        self.ui.tableWidget.setItem(
            rowCount, 1, QtGui.QTableWidgetItem(str(file_size)))
        self.ui.tableWidget.setItem(
            rowCount, 2, QtGui.QTableWidgetItem(str(file_progress)))

    def update_download_progress(self, file_progress):
        QtCore.QCoreApplication.processEvents()
        rowCount = self.ui.tableWidget.rowCount() - 1
        self.ui.tableWidget.setItem(
            rowCount, 2, QtGui.QTableWidgetItem(str(file_progress)))

    def update_status(self, status):
        self.ui.label_2.setText(str(status))

    def show_success_message(self, Message):
        QtGui.QMessageBox.information(self, "Pl-dl success", str(Message))
    
    def show_error_message(self, Message):
        QtGui.QMessageBox.critical(self, "Pl-dl error", "Download Failed: {0}".format(str(Message)))

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = AppGui()
    window.show()
    window.activateWindow()
    window.raise_()
    sys.exit(app.exec_())
    app.quit()

