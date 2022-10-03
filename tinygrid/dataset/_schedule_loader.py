from array import array
from dataclasses import dataclass, field
import os
from socket import send_fds

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
      return 1

    # init Schedule obj
    ins = Instance()

    # For each line check tag and put data into model
    for line in lines:
      split_line = line.split(' ')

      # Turn all int that is in string form into int
      split_line = [int(i) if i.isdigit() else i for i in split_line]

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
        raise Exception("provided schedule was invalid")

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
          raise Exception("provided schedule was invalid")
        else:
          # Store it
          ppoi = split_line
      # sched ⟨# recurring scheduled⟩ ⟨# once-off scheduled⟩
      elif tag == "sched":
        # Check if the sched has been seen before
        if len(sched) != 0:
          raise Exception("provided schedule was invalid")
        else:
          # Store it
          sched = split_line

    if not is_schedule_valid(sche, [ppoi, sched]):
      raise Exception("provided schedule was invalid")
    return sche

def is_schedule_valid(sche: Schedule, params: list) -> bool:
  # Check if no recurring activities where scheduled
  if len(sche.re_act) == 0:
    return False
  if len(sche.batteries) == 0 and len(sche.once_act) == 0 and len(sche.re_act) == 0:
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

def is_schedule_line_valid(split_line: array) -> bool:
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
    # Check if act_id is integer
    if not isinstance(split_line[1], int):
      return False
    # Check if start_time is integer
    if not isinstance(split_line[2], int):
      return False
    # Check if n_room is integer
    if not isinstance(split_line[3], int):
      return False
    # Check if n_rooms match listed buildings length
    if len(split_line[4:]) != split_line[3]:
      return False
    # Check if building ids are integers
    for b_id in split_line[4:]:
      if not isinstance(b_id, int):
        return False
  elif tag == "sched":
    # Check length of line
    if len(split_line) == 6:
      return False
  elif tag == "ppoi":
    # Check length of line
    if len(split_line) == 3:
      return False
  # Check for different tags, but ignore empty lines
  elif tag != '':
    return False
  return True