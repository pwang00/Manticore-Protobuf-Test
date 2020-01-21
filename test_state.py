from state_pb2 import *
import unittest

def generate_test_states():

    """ 
    Generates 102 (simulated) ready, busy, killed states
    ready states have ID equivalent to 0 mod 3
    busy states have ID equivalent to 1 mod 3
    killed states have ID equivalent to 2 mod 3

    Busy and killed states are also given custom 'reasons' (i.e. messages) to describe 
    why the states have stopped executing instructions or why they have been killed.

    Busy states are given non-default IDs (.id) , wait times (.wait_time), and number of
    executing instructions (.num_executing).

    StateSet objects may be described as arrays of State objects, which may then be serialized
    and deserialized via protobuf.

    """

    busy_states = StateSet()
    ready_states = StateSet()
    killed_states = StateSet()

    for ready_id, busy_id, killed_id in map(lambda x: (x, x + 1, x + 2), range(0, 100, 3)):
        rstate = State()
        bstate = State()
        kstate = State()

        rstate.type = State.READY
        rstate.id = ready_id
        
        bstate.type = State.BUSY
        bstate.id = busy_id
        bstate.num_executing = 10
        bstate.wait_time = 2
        bstate.reason = "Timeout"

        kstate.type = State.KILLED
        kstate.id = killed_id
        kstate.reason = "Killed by user"

        ready_states.states.extend([rstate])
        busy_states.states.extend([bstate])
        killed_states.states.extend([kstate])

    return ready_states, busy_states, killed_states

class TestStateGeneration(unittest.TestCase):

    def test_state_creation_defaults(self):

        """ 
        Initiates a blank state and checks to see if default values 
        are correct
        """

        s = State()
        self.assertEqual(s.id, 0)
        self.assertEqual(s.type, State.READY)
        self.assertEqual(s.num_executing, 0)
        self.assertEqual(s.reason, "")
        self.assertEqual(s.wait_time, 0)

    def test_state_creation(self):

        """ 
        Initiates a (non-default) busy state and checks to see if values 
        are passed in and updated successfully
        """
        s = State()
        s.id = 100
        s.type = State.BUSY
        s.num_executing = 5
        s.reason = "Execution terminated"
        s.wait_time = 10

        self.assertEqual(s.id, 100)
        self.assertEqual(s.type, State.BUSY)
        self.assertEqual(s.num_executing, 5)
        self.assertEqual(s.reason, "Execution terminated")
        self.assertEqual(s.wait_time, 10)

    def test_serialization(self):
        """ 
        Tests to see if serialization / deserialization works properly for State objects
        """
        s = State()
        s.id = 100
        s.type = State.BUSY
        s.num_executing = 5
        s.reason = "Execution terminated"
        s.wait_time = 10

        serialized = s.SerializeToString()
        s2 = State()
        s2.ParseFromString(serialized)

        self.assertEqual(s, s2)

    def test_StateSet(self):
        """ 
        Initiates 3 StateSets using the function above and checks to see if State values 
        are passed in and updated successfully
        """
        ready, busy, killed = generate_test_states()

        for ready_state in ready.states:
            self.assertEqual(ready_state.id % 3, 0)
            self.assertEqual(ready_state.type, State.READY)
            self.assertEqual(ready_state.num_executing, 0)
            self.assertEqual(ready_state.reason, "")
            self.assertEqual(ready_state.wait_time, 0)

        for busy_state in busy.states:
            self.assertEqual(busy_state.id % 3, 1)
            self.assertEqual(busy_state.reason, "Timeout")
            self.assertEqual(busy_state.type, State.BUSY)
            self.assertEqual(busy_state.num_executing, 10)
            self.assertEqual(busy_state.wait_time, 2)

        for killed_state in killed.states:
            self.assertEqual(killed_state.id % 3, 2)
            self.assertEqual(killed_state.type, State.KILLED)
            self.assertEqual(killed_state.num_executing, 0)
            self.assertEqual(killed_state.reason, "Killed by user")
            self.assertEqual(killed_state.wait_time, 0)

    def test_StateSet_Serialization(self):
        """ 
        Tests to see if serialization/deserialization works properly for StateSet objects
        """
        ready, busy, killed = generate_test_states()

        ready_serialized = ready.SerializeToString()
        busy_serialized = busy.SerializeToString()
        killed_serialized = killed.SerializeToString()

        ready_deserialized = StateSet()
        busy_deserialized = StateSet()
        killed_deserialized = StateSet()
        
        ready_deserialized.ParseFromString(ready_serialized) 
        busy_deserialized.ParseFromString(busy_serialized)
        killed_deserialized.ParseFromString(killed_serialized)

        self.assertEqual(ready_deserialized, ready)
        self.assertEqual(busy_deserialized, busy)
        self.assertEqual(killed_deserialized, killed)


if __name__ == "__main__":
    unittest.main()
