import npyscreen
import curses
import drawille
import logging
import select
import socket
import warnings

from state_pb2 import *
from format_states import *
from google.protobuf.message import DecodeError

warnings.filterwarnings("ignore")

class ManticoreTUI(npyscreen.NPSApp):

    def __init__(self):
        # List of all received states and messages
        self.all_states = []
        self.all_messages = []

        self.keypress_timeout_default = 1
        logging.basicConfig(filename="mcore_tui_logs",
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

        self._logger = logging.getLogger(__name__)
        self._connected = False

    def draw(self):
        # Draws the main TUI form with all sub-widgets and allows for user interaction
        self.MainForm = ManticoreMain(parentApp=self, name="Manticore TUI")
        self.prev_width, self.prev_height = drawille.getTerminalSize()
        self.MainForm.edit()

    def while_waiting(self):
        # Saves current terminal size to determine whether or not a redraw
        # of the TUI is necessary
        curr_width, curr_height = drawille.getTerminalSize()

        # Serialized data to be received from manticore server
        serialized = None

        try:

            # Attempts to (re)connect to manticore server 
            if not self._connected:
                self._mcore_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._logger.info("Connected to manticore server")
                self._mcore_socket.connect(("127.0.0.1", 1337))
                self._connected = True 
                self._socket_list = [self._mcore_socket]  

            # Uses Python select module with timeout 0 to determine whether or not sockets have any data
            # To be read from or written to to prevent client send/recv operations from blocking.
            read_sockets, write_sockets, error_sockets = select.select(self._socket_list, self._socket_list, [], 0)
            

            # If there are sockets available for reading, deserialize data
            if len(read_sockets):
                serialized = self._mcore_socket.recv(1024)
                self._logger.info("Received serialized of length {}".format(len(serialized)))

            # If there are sockets available for writing, send an ACK to server
            if len(write_sockets):
                self._mcore_socket.send(b"Received states")

            # Protobuf can't directly determine the type of data being received, so we use the following workaround
            # We first try to deserialize data as a StateList object and check its .states attribute
            # Since in practice a StateList must contain at least one state, we know that if len(.states) is 0
            # Then the deserialized message can't be a StateList.  We then try deserializing into a MessageList object
            # and check its .messages attribute.  If len(.messages) is empty, then we conclude that the data sent
            # was corrupted or incorrectly serialized.
            try:
                m = StateList()
                m.ParseFromString(serialized)

                if len(m.states) > 0: 
                    self.all_states += format_states(m)
                    self._logger.info("Deserialized StateList")

                else:
                    m = MessageList()
                    m.ParseFromString(serialized)
                    self.all_messages += format_messages(m)
                    self._logger.info("Deserialized LogMessage")

                    if len(m.messages) == 0:
                        raise TypeError

            except DecodeError:
                self._logger.info("Unable to deserialize message, malformed response")

        # Detect server disconnect
        except socket.error:
            self._connected = False

        # Handle any other exceptions
        except:
            pass

        self.MainForm.connection_text.value = f"{'Connected' if self._connected else 'Not connected'}"

        if curr_width != self.prev_width or curr_height != self.prev_height:        
            self._logger.info('Size changed')
            self.MainForm.erase()
            self.draw()
            self.MainForm.DISPLAY()

        # Updates the list of states and messages to be displayed 
        # Normally appending to the list of values during while_waiting() would work but we have to
        # Consider the scenario where the user resizes the terminal, in which case 
        # .erase() is called and all widgets lose their previous values upon being redrawn.
        # So we maintain a separate list of all currently received states and messages (all_states, all_messages)
        # and reassign Each widget's list of states / messages instead.

        self.MainForm.states_widget.entry_widget.values = self.all_states
        self.MainForm.messages_widget.entry_widget.values = self.all_messages
        
        self.MainForm.states_widget.name = f"Internal States ({len(self.MainForm.states_widget.values)} received)"
        self.MainForm.messages_widget.name = f"Log Messages ({len(self.MainForm.messages_widget.values)} received)"        
        
        self.MainForm.states_widget.display()
        self.MainForm.messages_widget.display()
        self.MainForm.connection_text.display()
        
    def main(self):
        self.draw()

class ManticoreMain(npyscreen.ActionForm):

    def create(self):
        # Draws a form with a widget for states, log messages, and connection status
        column_height = drawille.getTerminalSize()[::-1][0]

        self.states_widget = self.add(
                npyscreen.BoxTitle,
                name = "Internal States ({} received)",
                max_height = column_height // 3,
                editable=True
        )


        self.messages_widget = self.add(
                npyscreen.BoxTitle,
                name = "Log Messages",
                max_height = column_height // 3,
                editable=True,
        )

        self.connection_text = self.add_widget(npyscreen.TitleText, 
            name = f"Connection Status: ",
            editable = False)

    def on_ok(self):
        exit()

def main():
    manticore_TUI = ManticoreTUI()
    manticore_TUI.run()

if __name__ == "__main__":
    main()
