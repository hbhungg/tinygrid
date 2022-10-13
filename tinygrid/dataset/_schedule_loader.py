from dataclasses import dataclass, field
from distutils.command.build import build
import os
from typing import Any

# NOTES: Can both of them merge? Might be confuse if merged since instance and schedule need different data.
# Class for Instance
@dataclass
class BuildingInstance:
  n_small: int
  n_large: int

@dataclass
class BatteryInstance:
  capacity:   int
  max_power:  int
  efficiency: int
  building_id: int

@dataclass
class ActivityInstance:
  n_room:   int
  size:     str
  load:     int
  duration: int
  value:    int
  penalty:  int
  prec:     list[int] = field(default_factory=list)

@dataclass
class Instance:
  buildings: dict[int, BuildingInstance] = field(default_factory=dict)
  solars:    dict[int, int] = field(default_factory=dict)
  batteries: dict[int, BatteryInstance] = field(default_factory=dict)
  re_act:    dict[int, ActivityInstance] = field(default_factory=dict)
  once_act:  dict[int, ActivityInstance] = field(default_factory=dict)

# Class for Schedule (solution)
@dataclass
class BatterySchedule:
  time:     int
  decision: int

@dataclass
class ActivitySchedule:
  start_time:  int
  n_room:      int
  building_id: list[int] = field(default_factory=list)

@dataclass
class Schedule:
  re_act:   dict[int, ActivitySchedule] = field(default_factory=dict)
  once_act: dict[int, ActivitySchedule] = field(default_factory=dict)
  batteries:  dict[int, list[BatterySchedule]] = field(default_factory=dict)


def instance_parser(f_name: str) -> Instance:
    """
    Parse the instance.txt file according to the IEEE-CIS's Data_Description.pdf in docs
    Params:
      f_name: path to file
    Return: 
      Instance object.
    """
    lines = []
    if os.path.exists(f_name):
      with open(f_name) as f:
        lines = f.read().splitlines()
    else:
      raise Exception("file " + f_name + " does not exist.")

    # Seen ppoi tag
    ppoi = []

    # init Schedule obj
    ins = Instance()

    # For each line check tag and put data into model
    for line in lines:
      split_line = line.split(' ')

      # Turn all int that is in string form into int
      split_line = [int(i) if i.isdigit() else i for i in split_line]

      if not is_instance_line_valid(split_line):
        raise Line_exception("line in instance is invalid", line)

      tag = split_line[0]
      # b # building id # small # large
      if tag == "b":
        ins.buildings[split_line[1]] = \
          BuildingInstance(n_small=split_line[2], 
                   n_large=split_line[3])

      # s # solar id # building id
      elif tag == "s":
        ins.solars[split_line[1]] = split_line[2]

      # c # battery id # building id # capacity kWh # max power kW # efficiency
      elif tag == "c":
        ins.batteries[split_line[1]] = \
          BatteryInstance( building_id = split_line[2],
                  capacity   = split_line[3],
                  max_power  = split_line[4],
                  efficiency = float(split_line[5]))

      # r # activity # precedences
      elif tag == "r":
        ins.re_act[split_line[1]] = \
          ActivityInstance(n_room   = split_line[2],
                   size     = split_line[3],
                   load     = split_line[4],
                   duration = split_line[5],
                   value    = 0,
                   penalty  = 0,
                   prec     = split_line[7:])

      # a # activity # $value # $penalty # precedences
      elif tag == "a":
        ins.once_act[split_line[1]] = \
          ActivityInstance(n_room   = split_line[2],
                   size     = split_line[3],
                   load     = split_line[4],
                   duration = split_line[5],
                   value    = split_line[6],
                   penalty  = split_line[7],
                   prec     = split_line[9:])
      # ppoi ⟨# buildings⟩ ⟨# solar⟩ ⟨# battery⟩ ⟨# recurring⟩ ⟨# once-off⟩
      elif tag == "ppoi":
        # Check if the ppoi has been seen before
        if len(ppoi) != 0:
          raise Instance_exception("provided instance has too many ppoi lines", ins)
        else:
          # Store it
          ppoi = split_line

    if not is_instance_valid(ins, ppoi):
      raise Instance_exception("provided instance was parsed, but invalid", ins)
    return ins

def schedule_parser(f_name: str) -> Schedule:
    """
    Parse the scedule.txt file according to the IEEE-CIS's Data_Description.pdf in docs
    Params:
      f_name: path to file
    Return: 
      Schedule object.
    """
    lines = []

    # Check if path exists
    if os.path.exists(f_name):
      with open(f_name) as f:
        lines = f.read().splitlines()
    else:
      raise Exception("file " + f_name + " does not exist.")

    # Seen ppoi tag and seen sched tag
    ppoi = []
    sched = []

    # init Schedule obj
    sche = Schedule()

    # For each line check tag and put data into model
    for line in lines:
      split_line = line.split(' ')

      # Turn all int that is in string form into int
      split_line = [int(i) if i.isdigit() else i for i in split_line]

      if not is_schedule_line_valid(split_line):
        raise Line_exception("line in schedule is invalid", line)

      tag = split_line[0]

      # c # battery id # time # decision
      if tag == "c":
        b = BatterySchedule(time = split_line[2], decision = split_line[3])
        if split_line[1] in sche.battery:
          sche.battery[split_line[1]].append(b)
        else:
          sche.battery[split_line[1]] = [b]

      # r # act_id # start_time # n_room # [buildings_id]
      elif tag == "r":
        sche.re_act[split_line[1]] = \
          ActivitySchedule(start_time = split_line[2],
                  n_room = split_line[3],
                  building_id = split_line[4:])

      # a # act_id # start_time # n_room # [buildings_id]
      elif tag == "a":
        sche.once_act[split_line[1]] = \
          ActivitySchedule(start_time = split_line[2],
                  n_room = split_line[3],
                  building_id = split_line[4:])
      # ppoi ⟨# buildings⟩ ⟨# solar⟩ ⟨# battery⟩ ⟨# recurring⟩ ⟨# once-off⟩
      elif tag == "ppoi":
        # Check if the ppoi has been seen before
        if len(ppoi) != 0:
          raise Schedule_exception("provided schedule has too many ppoi lines", sche)
        else:
          # Store it
          ppoi = split_line
      # sched ⟨# recurring scheduled⟩ ⟨# once-off scheduled⟩
      elif tag == "sched":
        # Check if the sched has been seen before
        if len(sched) != 0:
          raise Schedule_exception("provided schedule has too many sched lines", sche)
        else:
          # Store it
          sched = split_line

    if not is_schedule_valid(sche, [ppoi, sched]):
      raise Schedule_exception("provided schedule was parsed, but invalid", sche)
    return sche

def is_schedule_valid(sche: Schedule, params: list) -> bool:
  # Check if no recurring activities where scheduled
  if len(sche.re_act) == 0:
    return False
  
  # Unpack variables
  ppoi = params[0]
  sched = params[1]

  # Check their lengths
  if len(ppoi) != 6 or len(sched) != 3:
    return False
  # Check if ppoi elements (apart from tag) are all integers
  for el in ppoi[1:]:
    if not isinstance(el, int):
      return False
  # Check if sched elements (apart from tag) are all integers
  for el in sched[1:]:
    if not isinstance(el, int):
      return False
  # Check if number of sched elements match the number received
  if len(sche.re_act) != sched[1] or len(sche.once_act) != sched[2]:
    return False
  return True

def is_schedule_line_valid(split_line: list) -> bool:
  tag = split_line[0]
  if tag == "c":
    # Check length of battery line
    if len(split_line) != 4:
      return False
    # Check if battery_id is integer
    if not isinstance(split_line[1], int):
      return False
    # Check if time is integer
    if not isinstance(split_line[2], int):
      return False    
    # Check if decision is in [0, 1, 2] as integer
    if (not isinstance(split_line[3], int)) or (split_line[3] not in [0,1,2]):
      return False
  elif tag == "r" or tag == "a":
    # Check length of activity line
    if len(split_line) < 4:
      return False
    for i in range(1, 4):
      if not isinstance(split_line[i], int):
        return False
    # Check if n_rooms match listed buildings length
    if len(split_line[4:]) != split_line[3]:
      return False
    # Check if building ids are integers
    for b_id in split_line[4:]:
      if not isinstance(b_id, int):
        return False
  # Check for different tags, but ignore empty lines
  elif tag != '' and tag != "sched" and tag != "ppoi":
    return False
  return True

def is_instance_line_valid(split_line: list) -> bool:
  tag = split_line[0]
  
  # b # building id # small # large
  if tag == 'b':
    if len(split_line) != 4:
      return False
    for i in range(1,len(split_line)):
      if not isinstance(split_line[i], int):
        return False 
  # s # solar id # building id
  elif tag == 's':
    if len(split_line) != 3:
      return False
    for i in range(1,len(split_line)):
      if not isinstance(split_line[i], int):
        return False 
  # c # battery id # building id # capacity kWh # max power kW # efficiency
  elif tag == 'c':
    if len(split_line) != 6:
      return False
    for i in range(1,len(split_line) - 1):
      if not isinstance(split_line[i], int):
        return False 
    if not is_float(split_line[5]):
      return False
  # r ⟨act. id⟩ ⟨# rooms⟩ ⟨{S, L} room size⟩ ⟨load kW⟩ ⟨duration⟩ ⟨# precedences⟩ ⟨act. Id⟩∗
  elif tag == 'r':
    if len(split_line) < 7:
      return False
    for i in [1,2,4,5,6]:
      if not isinstance(split_line[i], int):
        return False
    if split_line[6] != len(split_line[7:]):
      return False
    if split_line[3] not in ['S','L']:
      return False
  # a # activity # $value # $penalty # precedences
  elif tag == 'a':
    if len(split_line) < 9:
      return False
    for i in [1,2,4,5,6,7]:
      if not isinstance(split_line[i], int):
        return False
    if split_line[8] != len(split_line[9:]):
      return False
    if split_line[3] not in ['S','L']:
      return False
  elif tag != '' and tag != "ppoi":
    return False
  return True

def is_instance_valid(ins: Instance, ppoi: list) -> bool:
  # Check if there are buildings, solars, batteries, activities
  if len(ins.buildings) == 0 or len(ins.solars) == 0 or len(ins.batteries) == 0 or len(ins.re_act) == 0 or len(ins.once_act) == 0:
    return False
  if len(ppoi) != 6:
    return False

  # Check if the ppoi matches the instance loaded
  if len(ins.batteries) != ppoi[3] or len(ins.buildings) != ppoi[1] or len(ins.once_act) != ppoi[5] or len(ins.re_act) != ppoi[4] or len(ins.solars) != ppoi[2]:
    return False

  return True

class Line_exception():
  def __init__(self, message, line):
    self.message = message
    self.line = line
  def __str__(self):
    return self.message

class Schedule_exception():
  def __init__(self, message, sche):
    self.message = message
    self.sched = sche
  def __str__(self):
    return self.message

class Instance_exception():
  def __init__(self, message, ins):
    self.message = message
    self.ins = ins
  def __str__(self):
    return self.message

# FROM https://stackoverflow.com/questions/736043/checking-if-a-string-can-be-converted-to-float-in-python
def is_float(element: Any) -> bool:
    try:
        float(element)
        return True
    except ValueError:
        return False