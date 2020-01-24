from state_pb2 import *

def format_states(deserialized):
	updated = []
	template = "State id: {:<6d}\t\t Type: {:<8}\t Status: "
	types = {0: "READY", 1: "BUSY", 2: "KILLED"}
	
	for state in deserialized.states:
		to_add = template.format(
			state.id,
			types[state.type],
		)

		if state.type == State.BUSY:
			if state.num_executing and not (state.wait_time or state.reason):
				to_add += f"EXECUTING ({state.num_executing} instructions)"

			elif state.wait_time and not (state.num_executing or state.reason):
				to_add += f"WAITING ({state.wait_time} secs)"

			else:
				to_add += f"STOPPED ({state.reason})"

		else:
			to_add += f"{types[state.type]} (Not Busy)"

		updated += [to_add]

	return updated

def format_messages(deserialized):
	updated = []
	
	for message in deserialized.messages:
		updated += ["Content: \t\t{:<100s}".format(message.content)]

	return updated
