from PyQt5 import QtWidgets
import configparser
from PyQt5.QtCore import *
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5 import uic
from manualreview import videoscriptcore
from manualreview import videoeditor
from manualreview import client
from manualreview import publishmenu
class ScriptsMenu(QMainWindow):

    edit_response_false = pyqtSignal()
    edit_response_true = pyqtSignal()
    update_table = pyqtSignal()
    reset_editing_status = pyqtSignal()

    def __init__(self, username):
        QWidget.__init__(self)
        uic.loadUi("UI/rawscripts.ui", self)
        self.loggedinas.setText("Logged in as: %s" % username)
        self.treeWidget.currentItemChanged.connect(self.changeSelected)
        self.startEditing.clicked.connect(self.startVideoEditor)
        self.refreshScripts.clicked.connect(self.addRawScriptsToTree)
        self.flagComplete.clicked.connect(lambda : self.flagScript("MANUALCOMPLETE"))
        self.flagscriptquality.clicked.connect(lambda : self.flagScript("BAD"))
        self.update_table.connect(self.updateColors)
        self.reset_editing_status.connect(self.resetEditingStatus)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(4000)
        self.currentScriptSelected = None
        self.isEditing = False

    def flagScript(self, flagtype):
        if self.currentScriptSelected is not None:
            if flagtype == "MANUALCOMPLETE":
                title = "Warning, you are about to flag a Script"
                message = "You are about to flag script %s with a MANUALCOMPLETE tag \n"
                message += "A MANUALCOMPLETE tag means that this script " \
                           "has been completed outside of our system, " \
                           "and that there is no longer any need for it to appear here"
                self.createPopup("Warning", QMessageBox.Information, title, message)
                QMessageBox.Ok | QMessageBox.Cancel
                if self.retMsg == QMessageBox.Ok:
                    client.flagscript(self.currentScriptSelected, "MANUALCOMPLETE")
                elif self.retMsg == QMessageBox.Cancel:
                    pass
        else:
            print("Current selected script number return a None")

    def updateTime(self):
        self.changeSelected()

    def startVideoEditor(self):
        if hasattr(self, "currentTreeWidget"):
            scriptName = self.currentTreeWidget.text(0)
            scriptNo = scriptName.replace("script", "")
            indexSelectedScript = videoscriptcore.getScripts().index(int(scriptNo))
            selectedScript = videoscriptcore.video_scripts[indexSelectedScript]
            client.editScript(selectedScript.scriptno)
            self.videoEditorWindow = videoeditor.VideoEditor(selectedScript, self)
            self.videoEditorWindow.show()
            self.isEditing = True

    def resetEditingStatus(self):
        self.isEditing = False

    def changeSelected(self):
        try:
            if not self.treeWidget.currentItem().text(0) in videoscriptcore.getCategories():
                scriptName = self.treeWidget.currentItem().text(0)
                scriptNo = scriptName.replace("script", "")
                indexSelectedScript = videoscriptcore.getScripts().index(int(scriptNo))
                status = videoscriptcore.video_scripts[indexSelectedScript].status
                if hasattr(self, "currentTreeWidget"):


                    if status == "RAW":
                        self.currentTreeWidget.setForeground(0, QtGui.QBrush(QtGui.QColor("black")))
                        self.startEditing.setEnabled(True)
                        self.flagComplete.setEnabled(True)
                        self.flagscriptquality.setEnabled(True)
                    elif status == "EDITING":
                        self.currentTreeWidget.setForeground(0, QtGui.QBrush(QtGui.QColor("yellow")))
                        self.startEditing.setEnabled(False)
                        self.flagComplete.setEnabled(False)
                        self.flagscriptquality.setEnabled(False)
                    elif status == "COMPLETE":
                        self.currentTreeWidget.setForeground(0, QtGui.QBrush(QtGui.QColor("green")))
                        self.startEditing.setEnabled(False)
                        self.flagComplete.setEnabled(False)
                        self.flagscriptquality.setEnabled(False)
                    elif status == "MANUALCOMPLETE":
                        self.currentTreeWidget.setForeground(0, QtGui.QBrush(QtGui.QColor("darkgreen")))
                        self.startEditing.setEnabled(False)
                        self.flagComplete.setEnabled(False)
                        self.flagscriptquality.setEnabled(False)
                    if self.isEditing:
                        self.startEditing.setEnabled(False)

                self.updateDetailScreen()
        except AttributeError:
            self.updateDetailScreen()

    def updateDetailScreen(self):
        self.textBrowser.clear()
        self.currentTreeWidget = self.treeWidget.currentItem()
        try:
            scriptName = self.currentTreeWidget.text(0)
            scriptNo = scriptName.replace("script", "")
            indexSelectedScript = videoscriptcore.getScripts().index(int(scriptNo))
            selectedScript = videoscriptcore.video_scripts[indexSelectedScript]
            self.currentScriptSelected = selectedScript.scriptno
            self.textBrowser.append("Category: %s\n"%selectedScript.sub_reddit)
            self.textBrowser.append("Title: %s\n"%selectedScript.title)
            self.textBrowser.append("Upvotes: %s"%selectedScript.upvotes)
            self.textBrowser.append("Author: %s"%selectedScript.author)
            self.textBrowser.append("Vid Number: %s"%selectedScript.vidNo)
            self.textBrowser.append("Status: %s"%selectedScript.status)
            self.textBrowser.append("Script ID: %s"%selectedScript.scriptno)
            self.textBrowser.append("Being Edited by: %s"%selectedScript.editedby)
            self.editedby.setText(selectedScript.editedby)
            self.currentTreeWidget.setForeground(0, QtGui.QBrush(QtGui.QColor("blue")))
        except AttributeError:
            pass
        self.updateColors()


    def updateColors(self):
        children = self.count_tems()
        for i in range(len(children)):
            scriptName = children[i].text(0)
            scriptNo = scriptName.replace("script", "")
            indexSelectedScript = videoscriptcore.getScripts().index(int(scriptNo))
            status = videoscriptcore.video_scripts[indexSelectedScript].status
            if hasattr(self, "currentTreeWidget"):
                if status == "RAW":
                    children[i].setForeground(0, QtGui.QBrush(QtGui.QColor("black")))
                elif status == "EDITING":
                    children[i].setForeground(0, QtGui.QBrush(QtGui.QColor("yellow")))
                elif status == "COMPLETE":
                    children[i].setForeground(0, QtGui.QBrush(QtGui.QColor("green")))
                elif status == "MANUALCOMPLETE":
                    children[i].setForeground(0, QtGui.QBrush(QtGui.QColor("darkgreen")))

    def count_tems(self):
        count = 0
        iterator = QtWidgets.QTreeWidgetItemIterator(self.treeWidget)  # pass your treewidget as arg
        items = []
        while iterator.value():
            item = iterator.value()

            if item.parent():
                if item.parent().isExpanded():
                    count += 1
                    items.append(item)

            else:
                # root item
                count += 1
            iterator += 1

        return items
    def addRawScriptsToTree(self):
        self.treeWidget.clear()
        for i, vid in enumerate(videoscriptcore.video_scripts):
            new_item = self.addChild(vid.sub_reddit, "script%s"%vid.vidNo)
            if vid.status == "EDITING":
                new_item.setForeground(0, QtGui.QBrush(QtGui.QColor("yellow")))
            elif vid.status == "RAW":
                new_item.setForeground(0, QtGui.QBrush(QtGui.QColor("black")))
            elif vid.status == "COMPLETE":
                new_item.setForeground(0, QtGui.QBrush(QtGui.QColor("green")))
            elif vid.status == "MANUALCOMPLETE":
                new_item.setForeground(0, QtGui.QBrush(QtGui.QColor("darkgreen")))

        self.treeWidget.expandToDepth(0)

    def resetColor(self):
        for i in range(self.treeWidget.topLevelItemCount()):
            #for y in range(self.treeWidget.)
            self.treeWidget.topLevelItem(i).setForeground(i, QtGui.QBrush(QtGui.QColor("black")))

    def getAllTopLevel(self):
        items = []
        for index in range(self.treeWidget.topLevelItemCount()):
            items.append(self.treeWidget.topLevelItem(index))
        return items

    def addTopLevel(self, name):
        if self.getTopLevelByName(name) is None:
            QTreeWidgetItem(self.treeWidget, [name])

    def addChild(self, parent, child):
        self.addTopLevel(parent)
        return QTreeWidgetItem(self.getTopLevelByName(parent), [child])

    def getTopLevelByName(self, name):
        for index in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(index)
            if item.text(0) == name:
                return item
        return None

    def closeEvent(self, event):
        if hasattr(self, "videoEditorWindow"):
            self.videoEditorWindow.close()
        if not publishmenu.currentPublishMenu is None:
            publishmenu.currentPublishMenu.close()
        self.close()
        client.safeDisconnect()

    def createPopup(self, messagetype, icon, text, message):
        self.msg = QMessageBox()
        self.msg.setIcon(icon)
        self.msg.setText(text)
        self.msg.setInformativeText(message)
        self.msg.setWindowTitle(messagetype)
        if messagetype == "Error":
            self.msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Close)
        if messagetype == "Warning":
            self.msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        else:
            self.msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Close)
        self.retMsg = self.msg.exec_()


