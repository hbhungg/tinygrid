from datetime import datetime, timedelta

from ortools.sat.python import cp_model

from ..utils import Const, date_range, weekday_range, first_dow, first_week_map
from ..dataset._schedule_loader import Instance, Schedule, BatterySchedule, ActivitySchedule


def optimizer(instance: Instance, warm_start: Schedule, 
              start_time: datetime, end_time:datetime,
              fix_start: bool=False): 

  # Init CP model
  model = cp_model.CpModel()

  # First week start and end day of month
  _, fmonday = first_dow(Const.MONDAY, start_time, end_time)
  ffriday_idx, ffriday = first_dow(Const.FRIDAY, start_time, end_time)
  # End of office hour is 17:00, so we add 17 hours.
  ffriday_end_office = ffriday + timedelta(hours=17)
  ffriday_idx_end_office = ffriday_idx + 17 * Const.PERIOD_IN_HOUR

  # **********************************
  # *********** VARIABLES ************
  # **********************************

  # ****** Recurrence variables ******
  re_act_start_day = {}
  re_act_in_duration = {}
  re_act_start = {}
  for idx, act in instance.re_act.items():
    # Start day index for each activity
    re_act_start_day[idx] = \
      model.NewIntVar(1, 31, f"re_act_start_day_{idx}")

    # Binary for if activity is still in duration
    for tx, _ in weekday_range(start_time, ffriday_end_office, office=True):
      re_act_in_duration[(idx, tx)] = \
          model.NewBoolVar(f"re_act_in_duration_{idx}_{tx}")

    # Binary for if activity start at this time step
    for tx, _ in weekday_range(start_time, ffriday_end_office,
                               office=True, offset=act.duration):
      re_act_start[(idx, tx)] = \
          model.NewBoolVar(f"re_act_start_{idx}_{tx}")

  # ****** Once off variables ******
  once_act_start_day = {}
  once_act_in_duration = {}
  once_act_start = {}
  once_act_scheduled = {}
  for idx, act in instance.once_act.items():
    # Start day index for each activity
    once_act_start_day[idx] = \
        model.NewIntVar(1, 31, f"once_act_start_day_{idx}")
    # If a once activity is scheduled
    once_act_scheduled[idx] = \
        model.NewBoolVar(f"once_act_scheduled_{idx}")

    # Binary for if activity is still in duration
    for tx, _ in weekday_range(start_time, end_time, office=True):
      once_act_in_duration[(idx, tx)] = \
          model.NewBoolVar(f"once_act_in_duration_{idx}_{tx}")

    # Binary for if activity start at this time step
    for tx, _ in weekday_range(start_time, end_time, office=True, offset=act.duration):
      once_act_start[(idx, tx)] = \
          model.NewBoolVar(f"once_act_start_{idx}_{tx}")


  # ****** Battery variables ******
  #bat_charge = {}
  #bat_discharge = {}
  #bat_cap = {}
  #for idx, bat in instance.batteries.items():
  #  for tx, _ in enumerate(date_range(start_time, end_time)):
  #    # Batteries charge action time step t
  #    bat_charge[(idx, tx)] = model.NewBoolVar(f"bat_c_{idx}_{tx}") 
  #    # Batteries discharge action time step t
  #    bat_discharge[(idx, tx)] = model.NewBoolVar(f"bat_d_{idx}_{tx}") 
  #    # Battery capacity at time step t
  #    bat_cap[(idx, tx)] = model.NewIntVar(0, bat.capacity, f"bat_c_{idx}_{tx}")


  # **********************************
  # ********** CONSTRAINT ************
  # **********************************

  # ****** Recurrence activity constraint ******
  offset_start = start_time.time().hour * 4 + start_time.time().minute//15
  for idx, act in instance.re_act.items():
    temp = []
    st = 0

    for tx, _ in weekday_range(start_time, ffriday_end_office,
                               office=True, offset=act.duration):
      temp.append(re_act_start[(idx, tx)])
      # Day index that activity start
      st += (tx + offset_start)//Const.PERIOD_IN_DAY * re_act_start[(idx, tx)]

    # Recurrence activity must be schedule, and schedule once
    model.AddExactlyOne(temp)
    model.Add(re_act_start_day[idx] == st+1)

    # Activity in duration base on the start time
    for tx, _ in weekday_range(start_time, ffriday_end_office, office=True):
      zt = sum(re_act_start.get((idx, tt), 0) for tt in range(tx-act.duration+1, tx+1))
      model.Add(re_act_in_duration[(idx, tx)] == zt)

    # Precedences
    for prec in act.prec:
      model.Add(re_act_start_day[idx] > re_act_start_day[prec])

  
  # ****** Once-off activity constraint ******
  for idx, act in instance.once_act.items():
    temp = []
    st, wt = 0, 0

    for tx, _ in weekday_range(start_time, end_time, office=True, offset=act.duration):
      temp.append(once_act_start[(idx, tx)])
      # Day index that activity start
      st += (tx + offset_start)//Const.PERIOD_IN_DAY * once_act_start[(idx, tx)]
    #  wt += once_act_start[(idx, tx)]

    # Once off can be schedule once or not
    model.AddExactlyOne(temp)
    # If a particular once off activity is scheduled
    #model.Add(once_act_scheduled[idx] == wt)
    #model.Add(once_act_start_day[idx] == st+once_act_scheduled[idx])
    model.Add(once_act_start_day[idx] == st+1)

    # Activity in duration base on the start time
    for tx, _ in weekday_range(start_time, end_time, office=True):
      zt = sum(once_act_start.get((idx, tt), 0) for tt in range(tx-act.duration+1, tx+1))
      model.Add(once_act_in_duration[(idx, tx)] == zt)

    # Precedences
    for prec in act.prec:
      model.Add(once_act_start_day[idx] > once_act_start_day[prec])


  # ****** Room constraint ******
  # Total small and large room of all the buildings
  total_small_r = sum((i.n_small for i in instance.buildings.values()))
  total_large_r = sum((i.n_large for i in instance.buildings.values()))
  for (tx, _), txmf in zip(weekday_range(start_time, end_time),
                           first_week_map(start_time, end_time)):
    c_small, c_large = 0, 0

    for idx, act in instance.re_act.items():
      if act.size == "S": c_small += re_act_in_duration.get((idx, txmf), 0) * act.n_room
      if act.size == "L": c_large += re_act_in_duration.get((idx, txmf), 0) * act.n_room

    for idx, act in instance.once_act.items():
      if act.size == "S": c_small += once_act_in_duration.get((idx, tx), 0) * act.n_room
      if act.size == "L": c_large += once_act_in_duration.get((idx, tx), 0) * act.n_room
    model.Add(c_small <= total_small_r)
    model.Add(c_large <= total_large_r)


  # **********************************
  # ************ SOLVING *************
  # **********************************

  solver = cp_model.CpSolver()
  solver.parameters.num_search_workers = 10
  solver.parameters.log_search_progress = True
  status = solver.Solve(model)

  if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    retval = Schedule()

    total_small_r = sum((i.n_small for i in instance.buildings.values()))
    total_large_r = sum((i.n_large for i in instance.buildings.values()))
    small_rooms = [None] * total_small_r
    large_rooms = [None] * total_large_r
    small_bmap, large_bmap = [], []

    for idx, bd in instance.buildings.items():
      for i in range(bd.n_small): small_bmap.append(idx)
      for i in range(bd.n_large): large_bmap.append(idx)

    pair_tx_txmf = list(zip(weekday_range(start_time, end_time), first_week_map(start_time, end_time)))
    for prev_t, curr_t in zip(pair_tx_txmf, pair_tx_txmf[1:]):
      prev_tx = prev_t[0][0]
      curr_tx = curr_t[0][0]

      prev_txmf = prev_t[1]
      curr_txmf = curr_t[1]

      for tt in [True, False]:
        for idx, act in instance.re_act.items():
          # Activity in duration at t
          t0_status = solver.Value(re_act_in_duration.get((idx, curr_txmf), 0))
          # Activity in duration at t-1
          ts1_status = solver.Value(re_act_in_duration.get((idx, prev_txmf), 0))
          # Assign activity room to buildings
          small_rooms, large_rooms, bidxs = \
              _fill_or_remove_room(t0_status, ts1_status, tt, idx, 
                                   small_rooms, large_rooms, act, "r",
                                   small_bmap, large_bmap)

          # Write out the building assignment
          if bidxs is not None and curr_tx <= ffriday_idx_end_office:
            retval.re_act[idx] = ActivitySchedule(start_time=curr_tx, n_room=act.n_room, building_id=bidxs)

        for idx, act in instance.once_act.items():
          # Activity in duration at t
          t0_status = solver.Value(once_act_in_duration.get((idx, curr_tx), 0))
          # Activity in duration at t-1
          ts1_status = solver.Value(once_act_in_duration.get((idx, prev_tx), 0))
          # Assign activity room to buildings
          small_rooms, large_rooms, bidxs = \
              _fill_or_remove_room(t0_status, ts1_status, tt, idx, 
                                   small_rooms, large_rooms, act, "o",
                                   small_bmap, large_bmap)

          # Write out the building assignment
          if bidxs is not None:
            retval.once_act[idx] = ActivitySchedule(start_time=curr_tx, n_room=act.n_room, building_id=bidxs)

    return retval
  else:
    return None

def _fill_or_remove_room(t0_status, ts1_status, tt, idx, small_rooms, large_rooms, act, act_t, small_bmap, large_bmap):
  bidxs = None
  # t == 0 and t-1 == 1, means that activity has ended
  if t0_status == 0 and ts1_status == 1 and tt == True:
    if act.size == "S": small_rooms = _remove_room(small_rooms, (idx, act_t))
    if act.size == "L": large_rooms = _remove_room(large_rooms, (idx, act_t))
  # t == 1 and t-1 == 0, means that activity just started
  if t0_status == 1 and ts1_status == 0 and tt == False:
    if act.size == "S": small_rooms, bidxs = _fill_room(small_rooms, act.n_room, (idx, act_t), small_bmap)
    if act.size == "L": large_rooms, bidxs = _fill_room(large_rooms, act.n_room, (idx, act_t), large_bmap)
  return small_rooms, large_rooms, bidxs

def _fill_room(room_lst, n_room, val, bmap):
  bidxs = []
  for idx, v in enumerate(room_lst):
    if v is None:
      room_lst[idx] = val
      bidxs.append(bmap[idx])
      n_room -= 1
      if n_room == 0:
        return room_lst, bidxs
  assert n_room == 0, f"Not enough room to fill {val} {room_lst}"
  return room_lst, bidxs

def _remove_room(room_lst, val):
  for idx, v in enumerate(room_lst):
    if v == val:
      room_lst[idx] = None
  return room_lst


def save_schedule(path, schedule):
  with open(path, "w") as f:
    f.write("ppoi 6 6 2 50 20\n")
    f.write(f"sched {len(schedule.re_act)} {len(schedule.once_act)}\n")
    for idx, act in schedule.re_act.items():
      f.write(f'r {idx} {act.start_time} {act.n_room} {" ".join(map(str, act.building_id))}\n')
    for idx, act in schedule.once_act.items():
      f.write(f'a {idx} {act.start_time} {act.n_room} {" ".join(map(str, act.building_id))}\n')
