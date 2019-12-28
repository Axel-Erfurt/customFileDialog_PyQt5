#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QMainWindow, QApplication, QAction, QFileDialog, QSplitter, 
                            QVBoxLayout, QWidget, QDockWidget, QTreeView, QLineEdit, QPushButton, 
                            QHBoxLayout, QWidget, QFileSystemModel, QAbstractItemView)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize, QDir, QFileInfo, QStandardPaths
import os

class myFM(QWidget):
    def __init__(self):
        super(myFM, self).__init__()

        self.treeview = QTreeView()
        self.listview = QTreeView()
        
        self.treeview.clicked.connect(self.on_clicked)

        self.hiddenEnabled = False

        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.addWidget(self.treeview)
        self.splitter.addWidget(self.listview)

        hlay = QHBoxLayout()
        hlay.addWidget(self.splitter)

        self.wid = QWidget()
        self.wid.setLayout(hlay)
        self.mywid = QVBoxLayout()
        
        self.fileWid = QHBoxLayout()
        self.fileNameField = QLineEdit(placeholderText = "filename.ext")
        self.fileWid.addWidget(self.fileNameField)
        self.btnCancel = QPushButton("Cancel")
        self.btnCancel.setFixedWidth(100)
        self.btnSave = QPushButton("Save")
        self.btnSave.setFixedWidth(100)
        self.fileWid.addWidget(self.btnCancel)
        self.fileWid.addWidget(self.btnSave)
        self.mywid.addLayout(self.fileWid)
        self.mywid.addWidget(self.wid)
        self.setLayout(self.mywid)

        path = QDir.rootPath()


        self.dirModel = QFileSystemModel()
        self.dirModel.setReadOnly(True)
        self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Drives)
        self.dirModel.setRootPath(QDir.rootPath())

        self.fileModel = QFileSystemModel()
        self.fileModel.setReadOnly(True)
        self.fileModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs  | QDir.Files)
        self.fileModel.setResolveSymlinks(True)

        self.treeview.setModel(self.dirModel)
        self.treeview.selectionModel().selectionChanged.connect(self.on_treeviewSelectionChanged)
        self.treeview.hideColumn(1)
        self.treeview.hideColumn(2)
        self.treeview.hideColumn(3)

        self.listview.setModel(self.fileModel)
        self.listview.selectionModel().selectionChanged.connect(self.on_listviewSelectionChanged)
        self.treeview.setRootIsDecorated(True)

        self.listview.header().resizeSection(0, 320)
        self.listview.header().resizeSection(1, 80)
        self.listview.header().resizeSection(2, 80)
        self.listview.setSortingEnabled(True) 
        self.treeview.setSortingEnabled(True) 

        self.treeview.setRootIndex(self.dirModel.index(path))

        docs = QStandardPaths.standardLocations(QStandardPaths.DocumentsLocation)[0]
        self.treeview.setCurrentIndex(self.dirModel.index(docs))

        self.treeview.setTreePosition(0)
        self.treeview.setUniformRowHeights(True)
        self.treeview.setExpandsOnDoubleClick(True)
        self.treeview.setIndentation(12)
        self.treeview.sortByColumn(0, Qt.AscendingOrder)

        self.splitter.setSizes([20, 160])

        self.listview.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listview.setIndentation(10)
        self.listview.sortByColumn(0, Qt.AscendingOrder)
        

    def enableHidden(self):
        if self.hiddenEnabled == False:
            self.fileModel.setFilter(QDir.NoDotAndDotDot | QDir.Hidden | QDir.AllDirs | QDir.Files)
            self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.Hidden | QDir.AllDirs)
            self.hiddenEnabled = True
            print("set hidden files to true")
        else:
            self.fileModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)
            self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
            self.hiddenEnabled = False
            print("set hidden files to false")


    def on_clicked(self, index):
        if self.treeview.selectionModel().hasSelection():
            index = self.treeview.selectionModel().currentIndex()
            if not(self.treeview.isExpanded(index)):
                self.treeview.setExpanded(index, True)
            else:
                self.treeview.setExpanded(index, False)

    def on_treeviewSelectionChanged(self):
        if self.treeview.selectionModel().hasSelection():
            index = self.treeview.selectionModel().currentIndex()
            path = self.dirModel.fileInfo(index).absoluteFilePath()
            self.listview.setRootIndex(self.fileModel.setRootPath(path))
            self.listview.selectionModel().clearSelection()
            
    def on_listviewSelectionChanged(self):
            self.treeview.selectionModel().clearSelection()
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).absoluteFilePath()
            if not os.path.isdir(path):
                fileinfo = QFileInfo(path)
                self.fileNameField.setText(fileinfo.fileName())


class mainWin(QMainWindow):
    def __init__(self, parent = None):
        super(mainWin, self).__init__(parent)
        self.setupUI()
        self.setupToolbar()
        self.setupStatusbar()
        self.setGeometry(0, 0, 800, 600)
        
        
    def setupUI(self):
        self.vbox = QVBoxLayout()
        self.cwid = QWidget()
        self.cwid.setLayout(self.vbox)
        self.setCentralWidget(self.cwid)
        self.setStyleSheet(myStyleSheet(self))
        self.fdock = QDockWidget("select File",  
                                features = QDockWidget.AllDockWidgetFeatures, 
                                allowedAreas = Qt.AllDockWidgetAreas)
        self.fmanager = myFM()
        self.fdock.setWidget(self.fmanager)
        self.fdock.setFixedHeight(450)
        self.fdock.setVisible(False)      
        self.addDockWidget(Qt.TopDockWidgetArea, self.fdock)
        
    def setupToolbar(self):
        tb = self.addToolBar("File")
        tb.setIconSize(QSize(16, 16))
        tb.setContextMenuPolicy(Qt.PreventContextMenu)
        tb.setFloatable(False)
        tb.setMovable(False)
        tb.addAction(QIcon.fromTheme('document-new'), "New", self.newFile)
        tb.addAction(QIcon.fromTheme('document-open'), "Open", self.openFile)
        tb.addAction(QIcon.fromTheme('document-save'), "Save", self.saveFile)
        tb.addAction(QIcon.fromTheme('document-save-as'), "Save as ...", self.saveFileAs)
        hiddenAct = QAction(QIcon.fromTheme('system-search'),"show / hide hidden files", self,
                            triggered=self.fmanager.enableHidden, shortcut="Ctrl+h")
        self.addAction(hiddenAct)
        
    def setupStatusbar(self):
        self.sbar = self.statusBar()
        self.sbar.showMessage("Ready", 0)
        
    def newFile(self):
        print("newFile")
        self.setWindowTitle("New")

    def saveFileAs(self, path=None):
        self.fdock.setVisible(True)
        self.fmanager.fileNameField.setVisible(True)
        self.fmanager.btnCancel.setVisible(True)
        self.fmanager.btnSave.setVisible(True)
        self.fmanager.fileNameField.setText(self.windowTitle())
        self.fmanager.fileNameField.returnPressed.connect(self.fileSaveSelected)
        self.fmanager.btnCancel.clicked.connect(lambda: self.fdock.setVisible(False))
        self.fmanager.btnSave.clicked.connect(self.fileSaveSelected)
        
    def saveFile(self):
        print("saveFile")
        
    def openFile(self, path=None):
        self.fdock.setVisible(True)
        self.fmanager.btnCancel.setVisible(True)
        self.fmanager.btnSave.setVisible(False)
        self.fmanager.btnCancel.clicked.connect(lambda: self.fdock.setVisible(False))
        self.fmanager.fileNameField.setVisible(False)
        self.fmanager.listview.doubleClicked.connect(self.fileSelected)
            
    def keyPressEvent(self, event):
        if event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier):
            if event.key() == Qt.Key_S:
                self.saveFileAs()
        elif event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_N:
                self.newFile()
            if event.key() == Qt.Key_O:
                self.openFile()
            if event.key() == Qt.Key_S:
                self.saveFile()
        else:
            event.accept()
            
    def fileSelected(self):
        index = self.fmanager.listview.selectionModel().currentIndex()
        path = self.fmanager.fileModel.fileInfo(index).absoluteFilePath()
        if not os.path.isdir(path):
            file_info = QFileInfo(path)
            self.setWindowTitle(file_info.baseName())
            # open code here
            self.fdock.setVisible(False)
        
    def fileSaveSelected(self):
        path = ''
        if self.fmanager.treeview.selectionModel().hasSelection():
            index = self.fmanager.treeview.selectionModel().currentIndex()
            path = self.fmanager.dirModel.fileInfo(index).absoluteFilePath()
        elif self.fmanager.listview.selectionModel().hasSelection():
            index = self.fmanager.listview.selectionModel().currentIndex()
            path = self.fmanager.fileModel.fileInfo(index).absoluteFilePath()
            if not os.path.isdir(path):
                path = os.path.dirname(path)
        fileName = self.fmanager.fileNameField.text()
        if fileName != "":
            fname = f"{path}/{fileName}"
            print(fname)
            # save code here
            file_info = QFileInfo(fname)
            self.setWindowTitle(file_info.baseName())
        self.fdock.setVisible(False)
            
def myStyleSheet(self):
    return """
QTextEdit
{
background: #eeeeec;
color: #202020;
}
QStatusBar
{
font-size: 8pt;
color: #555753;
}
QMenuBar
{
background: transparent;
border: 0px;
}
QToolBar
{
background: transparent;
border: 0px;
}
QMainWindow
{
     background: qlineargradient(y1: 0, y2: 1,
                                 stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                 stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
}
QLineEdit
{
     background: qlineargradient(y1: 0, y2: 1,
                                 stop: 0 #E1E1E1, stop: 0.4 #e5e5e5,
                                 stop: 0.5 #e9e9e9, stop: 1.0 #d2d2d2);
}
QPushButton
{
background: #D8D8D8;
}
QPushButton::hover
{
background: #729fcf;
}
QToolButton::hover
{
background: #729fcf;
}
    """       
  
        
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    win = mainWin()
    win.setWindowTitle("Main Window")
    win.show()

    sys.exit(app.exec_())