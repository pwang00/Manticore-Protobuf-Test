import npyscreen
import curses
import drawille
import logging
import select
import socket

from google.protobuf.message import DecodeError
from state_pb2 import *

class ManticoreTUI(npyscreen.NPSApp):

    def __init__(self):
        self.MainForm = None
        self.prev_width = None
        self.prev_height = None
        self.keypress_timeout_default = 1
        self.all_states = []
        self.all_messages = []
        self._connected = False
        
        logging.basicConfig(filename="mcore_tui_logs",
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

        self._logger = logging.getLogger(__name__)

        self._mcore_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._mcore_socket.connect(("127.0.0.1", 1337))
        self._connected = True
        self._logger.info("Connected to manticore server")

    def draw(self):
        self.MainForm = ManticoreMain(parentApp=self, name="Manticore TUI")
        self.prev_width, self.prev_height = drawille.getTerminalSize()
        self.MainForm.edit()

    def while_waiting(self):
        curr_width, curr_height = drawille.getTerminalSize()
        serialized = None
        self._socket_list = [self._mcore_socket]
        try:
            # Attempts to reestablish connection to manticore server

            read_sockets, write_sockets, error_sockets = select.select(self._socket_list, self._socket_list, [], 0)
            
            if len(read_sockets):
                serialized = self._mcore_socket.recv(1024)
                self._logger.info("Received serialized of length {}".format(len(serialized)))

            if len(write_sockets):
                self._mcore_socket.send(b"Received states")

            try:
                m = StateList()
                m.ParseFromString(serialized)

                if not len(m.states) > 0: 
                    raise WrongTypeException

                self.all_states += m.states
                self._logger.info("Deserialized StateList")

            except WrongTypeException:
                m = MessageList()
                m.ParseFromString(serialized)
                self.all_messages += m.messages
                self._logger.info("Deserialized LogMessage")
            except:
                self._logger.info("Unable to deserialize message, malformed response")
            
            self.MainForm.states_widget.entry_widget.values = self.all_states
            self.MainForm.messages_widget.entry_widget.values = self.all_messages

        except (socket.error, Exception) as e:
            self._connected = False

        self.MainForm.connection_text.value = f"{'Connected' if self._connected else 'Not connected'}"

        if curr_width != self.prev_width or curr_height != self.prev_height:
            self.all_states += self.MainForm.states_widget.entry_widget.values
            self.all_messages += self.MainForm.messages_widget.entry_widget.values            
            self._logger.info('Size changed')
            self.MainForm.erase()
            self.draw()
        else:    
            self.MainForm.DISPLAY()
        

    def main(self):
        self.draw()

class WrongTypeException(BaseException):
    def __init__(self):
        super().__init__("Deserialized type is incorrect")

class ManticoreMain(npyscreen.ActionForm):

    def create(self):
        column_height = drawille.getTerminalSize()[::-1][0]

        self.states_widget = self.add(
                npyscreen.BoxTitle,
                name = "Internal States",
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
