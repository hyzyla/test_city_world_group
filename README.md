# Test project City World Group

Simple socket server and GUI client.

Features:
- The server can listen to many clients at the same time.
- GUI client can create many clients.
- Message to the server or from the server can be any  size (sending via packets)
- GUI client listens to connections to the server and restarts all connections when one is failed.

Technology:
- PyQT5
- Python 3.6

![Screenshot](/doc/Screenshot.png)

For a run server, put into command shell this command:  `python server.py [port]`

For a run client, put into command shell this command:  `python GUI.py`
