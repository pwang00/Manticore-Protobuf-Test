# Serializable States

* See state.proto for current schema
* Examine and run `test_state.py` to verify that tests pass
* A basic client-server example demonstrating serialization over a socket is also provided in `client.py` and `server.py`

# TUI demo

* Open two separate terminal windows
* Run `python3 server_new.py` in one window
* Run `python3 tui.py` in another.
* Verify that after a certain amount of time, states are received (actually formatting the states for display purposes is a work in progress).

# Known issues

* npyscreen / curses sometimes flashes while updating the screen.
