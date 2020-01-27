# Serializable States

* See state.proto for current schema
* Examine and run `test_state.py` to verify that tests pass
* A basic client-server example demonstrating serialization over a socket is also provided in `client.py` and `server.py`

# TUI demo

* Open two separate terminal windows
* Run `python3 server_new.py` in one window
* Run `python3 tui.py` in another
* Verify that after a certain amount of time, both states and messages are received.

# TUI Features

* Detect when disconnect has happened and update connection status, and allow for reconnecting to server

# Known issues

* ~~npyscreen / curses sometimes flashes while updating the screen.~~

# TODO

* While the flashing issue has been fixed, there's no guarantee that throwing an exception won't accidentally mess up the TUI text.  As such, adding a hotkey to manually redraw the TUI may prove to be useful.
* Allow for users to configure logging levels
* Link to `mcorepv`
