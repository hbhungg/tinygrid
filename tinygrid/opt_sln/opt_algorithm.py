


# Battery schedualing
"""
Look at AEMO price data, perform charge at low price points.
Look at AEMO price data, perform discharge when activity allows.
No holds.
Batteries at 100% at start of month.
Battery can only charge from solar generation (need to check this)
"""

# Activity schedualing
"""
Once-off (9am to 5pm):
1. Put into activity ids into a directed (precedences) graph (matrix form).
2. Put activity into class which stores activity information addressed by activity id.
3. Look at possible activities avaiable for schedualing based on directed graph.
4. For each building with valid rooms amd valid room sizes: Look at each legal time t range: [t, t + (act_id.duration)]. In each range check if demand is low and if solar production is high.
   What low demand at time t means: Min_D_time = min{l=[t - 5, t + 5]}(Sum{k=l,l+act_id.duration}(energy_demand(k)))  
   What high solar production at time t means: Max_P_time = max{l=[t - 5, t + 5]}(Sum{k=l,l+act_id.duration}(solar_production(k)))
   Why choose +-5 as the range?: I have no idea, we can play with it.
   4.1. Choose C = min(Min_D_time, Max_P_time) as start time. May change this later.
5. Add act_id to lst of assigned activities in once-off, add details of it's assignment, such as time, buildings, rooms.(will assist in 4. seeing if time t is legal).
6. Apply battery discharge for activity.
7. Add new activites based on act_id as their precedence, force them to only to schedualed after time C.

Recurring (9am to 5pm):
1. Do same as once-off, but ignore once-off schedualing, and if there seems to be a conflict remove once-off, try place it into after hours 8pm to 8am if gain is non-negative.
"""