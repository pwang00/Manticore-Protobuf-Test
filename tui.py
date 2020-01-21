import npyscreen
import curses
import drawille
import logging

from state_pb2 import *
import socket

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

        # Say we reserve port 1337 for manticore?
        self._mcore_socket = socket.socket()
        self._mcore_socket.settimeout(10)

    def draw(self):
        self.MainForm = ManticoreMain(parentApp=self, name="Manticore TUI")
        self.prev_width, self.prev_height = drawille.getTerminalSize()

        self.MainForm.edit()

    def while_waiting(self):
        curr_width, curr_height = drawille.getTerminalSize()

        self.all_states += [self.MainForm.states_widget.entry_widget.values]
        self.all_messages += [self.MainForm.messages_widget.entry_widget.values]

        serialized = None
        deserialized_bytes = 0

        try:
            # Attempts to reestablish connection to manticore server
            if not self._connected: 
                self._mcore_socket.connect(("127.0.0.1", 1337))
                self._connected = True

            serialized = self._mcore_socket.recv(1024) # Serialized message

            if self._connected is True and len(serialized) == 0:
                raise EmptyRecvException

            try:
                m = StateSet()
                m.ParseFromString(serialized)
                self.all_states += m.states
                self._logger.info("Received serialized message")
            except google.protobuf.message.DecodeError:
                m = LogMessage()
                m.ParseFromString(serialized)
                self.all_messages += [m.content]
            except:
                self._logger.info("Unable to deserialize message, malformed response")
            
            self.MainForm.states_widget.entry_widget.values = self.all_states
            self.MainForm.messages_widget.entry_widget.values = self.all_messages

        except (socket.error, Exception, EmptyRecvException) as e:
            self._connected = False

        self.MainForm.connection_text.value = f"{'Connected' if self._connected else 'Not connected'}"

        if curr_width != self.prev_width or curr_height != self.prev_height:
            self._logger.info('Size changed')
            self.MainForm.erase()
            self.draw()

        self.MainForm.DISPLAY()
        

    def main(self):
        self.draw()

class EmptyRecvException(BaseException):
    def __init__(self):
        super().__init__("Received message of length 0")

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
