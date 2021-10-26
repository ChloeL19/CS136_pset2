import math

# Helper functions for our agents

def get_clicks(t, slot_id):
    '''
    Calculates the number of clicks expected in timestep t
    at position slot_id.
    - t: the current timestep
    - slot_id: the index of the current slot (position)

    returns: int, number of clicks
    '''
    cost_zero = round(30*math.cos((math.pi*t)/24) + 50)# the cost at slot 0 (the first slot)
    return round(0.75**slot_id*cost_zero)