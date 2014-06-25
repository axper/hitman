''' glob.py - Global variables

    This module contains only 1 variable called 'state'.
    It is used in many modules to access and modify program state and
    write to the html file.
    The definition of state variable can be found in module 'state_object.py'.
'''

# My modules
import init_deinit

state = init_deinit.initialize()
