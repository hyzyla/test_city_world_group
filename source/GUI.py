from __init__ import *
from client import Client

class ClientListItem(QWidget):

    def __init__(self, client):
        super().__init__()
        self.layout = QGridLayout()
        self.client = client
        self.status = "+" if self.client else "-"

        self.manage_button = QPushButton("Connect" if not self.client else "Disconnect", self)
        self.manage_button.clicked.connect(self.changeConnection)

        self.layout.addWidget(QLabel(str(self.client)), 0, 0)
        self.layout.addWidget(QLabel(self.status), 0, 1)
        self.layout.addWidget(self.manage_button, 0, 2)
        self.setLayout(self.layout)

    def changeConnection(self):
        if self.manage_button.text() == "Connect":
            self.client.changeStatus(connected=True)
        else:
            self.client.changeStatus(connected=False)


class ClientGUI(QWidget):

    def __init__(self):

        super().__init__()
        self.clients = []
        self.initUI()   

    def reconnectAll(self):
        print("RECONNECT ALL")
        need_to_connect = self.clients[:]

        while True:
            for client in need_to_connect:
                client.changeStatus(True)
                if client:
                    need_to_connect.remove(client)
            if not need_to_connect:    
                return
            time.sleep(1)

    def initUI(self):
      
        self.setWindowTitle('Client')
        self.configLayout()
        self.bindWidgets()
        self.show()


    def createClientsGroup(self):
        group_box = QGroupBox("Clients:")
        layout = QVBoxLayout()
        self.client_list = QListWidget()
        layout.addWidget(self.client_list)

        group_box.setLayout(layout)
        return group_box    

    def createNewClientsGroup(self):
        group_box = QGroupBox("New client:")

        self.host_line = QLineEdit(self)
        self.port_line = QLineEdit(self)
        self.add_button = QPushButton("Add", self)

        layout = QGridLayout()
        layout.setRowStretch(1,2)
        layout.addWidget(QLabel("Host"), 0, 0, 1, 1, Qt.AlignTop)
        layout.addWidget(QLabel("Port"), 0, 1, 1, 1, Qt.AlignTop)
        layout.addWidget(self.host_line, 1, 0, 1, 1, Qt.AlignTop)
        layout.addWidget(self.port_line, 1, 1, 1, 1, Qt.AlignTop)
        layout.addWidget(self.add_button, 1, 2, 1, 1, Qt.AlignTop)

        group_box.setLayout(layout)
        return group_box

    def createControlGroup(self):
        group_box = QWidget()

        self.clients_combobox = QComboBox()
        self.request_type_combobox = QComboBox()
        self.request_type_combobox.insertItems(0, ["ping", "status", "lower"])
        self.msg_line = QLineEdit()
        self.send_button = QPushButton("Send")
        self.log_textbox = QTextEdit()


        layout = QGridLayout()
        # first row
        layout.addWidget(QLabel("Select client:"), 0, 0)
        layout.addWidget(QLabel("Request type:"), 0, 1)
        layout.addWidget(QLabel("Massage:"), 0, 2)

        # second row
        layout.addWidget(self.clients_combobox, 1, 0)
        layout.addWidget(self.request_type_combobox, 1, 1)
        layout.addWidget(self.msg_line, 1, 2)
        layout.addWidget(self.send_button, 1, 3)

        # log 
        layout.addWidget(QLabel("Log:"), 2, 0, 1, 4)
        layout.addWidget(self.log_textbox, 3, 0, 1, 4)

        group_box.setLayout(layout)
        return group_box

    def configLayout(self):
        self.grid = QGridLayout(self)
        self.grid.addWidget(self.createClientsGroup(), 0, 0)
        self.grid.addWidget(self.createNewClientsGroup(), 0, 1)
        self.grid.addWidget(self.createControlGroup(), 1, 0, 1, 2)
        self.setLayout(self.grid)

    def addLogMsg(self, client, text):
        text = "[{c}]: {t}\n".format(c=client, t=text)
        self.log_textbox.moveCursor(QTextCursor.End)
        self.log_textbox.textCursor().insertText(text)


    def updateClientList(self):
        self.client_list.clear()
        for i, client in enumerate(self.clients):
            my_item = ClientListItem(client)
            item = QListWidgetItem()
            self.client_list.addItem(item)
            item.setSizeHint(my_item.sizeHint())
            self.client_list.setItemWidget(item, my_item)

    def updateCombobox(self):

        itemModel = QStandardItemModel()
        for i, client in enumerate(self.clients):
            if not client.connected:
                continue
            item = QStandardItem()
            item.setData(client, Qt.UserRole)
            item.setText(str(client))
            itemModel.appendRow(item)
        self.clients_combobox.setModel(itemModel)

    def updateAll(self):
        sender = self.sender()
        msg = "Connected" if sender else "Disconnected"

        # True if clients list is empty 
        if self.clients and not any(self.clients):
            threading.Thread(target=self.reconnectAll).start()

        self.addLogMsg(sender, msg)
        self.updateCombobox()
        self.updateClientList()

    def sendRequest(self):

        client = self.clients_combobox.currentData()
        request_type = str(self.request_type_combobox.currentText())
        massage = str(self.msg_line.text())
        full_massage = "{} {}".format(request_type, massage)

        if not client is None:
            response = client.sendRequest(full_massage)
            self.addLogMsg(client, "REQUEST: " + full_massage)
            self.addLogMsg(client, "RESPONSE: " + response)

    def disconnectAll(self):
        print("DISCONNECT ALL")
        for client in self.clients:
            client.changeStatus(connected=False)

    def addClient(self):
        if self.port_line.text():
            host = self.host_line.text()
            port = int(self.port_line.text())
            cl = Client(port, host)

            cl.connectionChanged.connect(self.updateAll)
            cl.connectionFailed.connect(lambda: self.addLogMsg(cl, "Connection failed"))

            upd_func = lambda: threading.Thread(target=self.disconnectAll).start()
            cl.connectionRefused.connect(upd_func)

            if cl:
                self.clients.append(cl)
                self.addLogMsg(cl, "Connected")
                self.updateClientList()
                self.updateCombobox()
            else:
                cl.connectionFailed.emit()

    def bindWidgets(self):
        self.add_button.clicked.connect(self.addClient)
        self.send_button.clicked.connect(self.sendRequest)
  

def kill_proc_tree(pid, including_parent=True):
    parent = psutil.Process(pid)
    for child in parent.children(recursive=True):
        child.kill()
    if including_parent:
        parent.kill()       
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = ClientGUI()
    app.exec_()

    me = os.getpid()
    kill_proc_tree(me)
