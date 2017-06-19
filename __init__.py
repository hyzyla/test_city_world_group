import struct
import sys
from PyQt5.QtWidgets import (QWidget, QToolTip, QComboBox, QScrollArea, QListWidget,
    QPushButton, QApplication, QGridLayout, QPushButton, QTextEdit, QListWidgetItem,
    QLineEdit, QLabel, QGroupBox, QVBoxLayout)

from PyQt5.QtCore import Qt, pyqtSignal,QObject
from PyQt5.QtGui import QTextCursor, QStandardItemModel, QStandardItem
import socket, threading, psutil, os, time

from PyQt5.QtGui import QFont    