from dataclasses import dataclass, field

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
  solars:    dict[int, int]      = field(default_factory=dict)
  batteries: dict[int, BatteryInstance]  = field(default_factory=dict)
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
  N_room:      int
  building_id: list[int]

@dataclass
class Schedule:
  re_act:   dict[int, ActivitySchedule]
  once_act: dict[int, ActivitySchedule]
  battery:  dict[int, BatterySchedule]


def instance_parser(f_name: str) -> Instance:
    """
    Parse the instance.txt file according to the IEEE-CIS's Data_Description.pdf
    Params:
      f_name: path to file
    Return: 
      Instance object.
    """
    lines = []

    with open(f_name) as f:
      lines = f.read().splitlines()

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
          BatteryInstance(capacity   = split_line[2],
                  max_power  = split_line[3],
                  efficiency = split_line[4])

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
    Parse the scedule.txt file according to the IEEE-CIS's Data_Description.pdf
    Params:
      f_name: path to file
    Return: 
      Schedule object.
    """
    lines = []

    with open(f_name) as f:
      lines = f.read().splitlines()

    # init Schedule obj
    sche = Schedule()

    # For each line check tag and put data into model
    for line in lines:
      split_line = line.split(' ')

      # Turn all int that is in string form into int
      split_line = [int(i) if i.isdigit() else i for i in split_line]

      tag = split_line[0]

      # c # battery id # time # decision
      if tag == "c":
        sche.batteries[split_line[1]] = \
          BatterySchedule(time = split_line[2],
                  decision = split_line[3])

      # r # act_id # start_time # n_rooms # [buildings_id]
      elif tag == "r":
        sche.re_act[split_line[1]] = \
          ActivityInstance(start_time = split_line[2],
                  n_rooms = split_line[3],
                  prec    = split_line[4:])

      # a # activity # $value # $penalty # precedences
      elif tag == "a":
        sche.once_act[split_line[1]] = \
          ActivityInstance(start_time = split_line[2],
                  n_rooms = split_line[3],
                  prec    = split_line[4:])

    return sche

