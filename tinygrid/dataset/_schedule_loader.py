from dataclasses import dataclass, field

@dataclass
class Building:
  n_small: int
  n_large: int

@dataclass
class Battery:
  capacity:   int
  max_power:  int
  efficiency: int

@dataclass
class Activity:
  n_room:   int
  size:     str
  load:     int
  duration: int
  value:    int
  penalty:  int
  prec:     list[int] = field(default_factory=list)

@dataclass
class Schedule:
  buildings: dict[int, Building] = field(default_factory=dict)
  solars:    dict[int, int]      = field(default_factory=dict)
  batteries: dict[int, Battery]  = field(default_factory=dict)
  re_act:    dict[int, Activity] = field(default_factory=dict)
  once_act:  dict[int, Activity] = field(default_factory=dict)

def schedule_parser(f_name: str) -> Schedule:
    """
    Parse the schedule .txt file according to the IEEE-CIS's Data_Description.pdf
    into Schedule class
    """
    lines = []

    with open(f_name) as f:
      lines = f.read().splitlines()

    # init Schedule obj
    schedule = Schedule()

    # For each line check tag and put data into model
    for line in lines:
      split_line = line.split(' ')

      # Turn all int that is in string form into int
      split_line = [int(i) if i.isdigit() else i for i in split_line]

      tag = split_line[0]
      # b # building id # small # large
      if tag == "b":
        schedule.buildings[split_line[1]] = \
          Building(n_small=split_line[2], 
                   n_large=split_line[3])

      # s # solar id # building id
      elif tag == "s":
        schedule.solars[split_line[1]] = split_line[2]

      # c # battery id # building id # capacity kWh # max power kW # efficiency
      elif tag == "c":
        schedule.batteries[split_line[1]] = \
          Battery(capacity   = split_line[2],
                  max_power  = split_line[3],
                  efficiency = split_line[4])

      # r # activity # precedences
      elif tag == "r":
        schedule.re_act[split_line[1]] = \
          Activity(n_room   = split_line[2],
                   size     = split_line[3],
                   load     = split_line[4],
                   duration = split_line[5],
                   value    = 0,
                   penalty  = 0,
                   prec     = split_line[7:])

      # a # activity # $value # $penalty # precedences
      elif tag == "a":
        schedule.once_act[split_line[1]] = \
          Activity(n_room   = split_line[2],
                   size     = split_line[3],
                   load     = split_line[4],
                   duration = split_line[5],
                   value    = split_line[6],
                   penalty  = split_line[7],
                   prec     = split_line[9:])

    return schedule

