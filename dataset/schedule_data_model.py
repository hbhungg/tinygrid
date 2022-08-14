from dataset.graph_data_model import Node, Edge, Digraph

class Schedule_Model:
  def __init__(self, phase: int, path: str) -> None:
    self.ppoi = {}
    self.buildings = []
    self.solars = []
    self.batteries = []
    self.f_path = path

    # activites
    self.acts = []
    self.once_off_acts = []

    # Phase in competition
    self.phase = phase

    # Check and set size tag on file
    self.size_tag = "large"
    sPath = path.split('/')
    if "small" in sPath[-1]:
      self.size_tag = "small"

  def add_ppoi(self, line_arr: str) -> None:
    self.ppoi = {
      "buildings": int(line_arr[1]),
      "solar": int(line_arr[2]),
      "battery": int(line_arr[3]),
      "recurring": int(line_arr[4]),
      "once-off": int(line_arr[5])
    }

  def add_building(self, line_arr: str) -> None:
    temp = {
      "building_id": line_arr[1],
      "num_small_rooms": int(line_arr[2]),
      "num_large_rooms": int(line_arr[3])
    }
    self.buildings.append(temp)

  def add_solar(self, line_arr: str) -> None:
    temp = {
      "solar_id": line_arr[1],
      "building_id": line_arr[2]
    }
    self.solars.append(temp)

  def add_battery(self, line_arr: str) -> None:
    temp = {
      "battery_id": line_arr[1],
      "building_id": line_arr[2],
      "capacity_kWh": float(line_arr[3]),
      "max_power_kW": float(line_arr[4]),
      "efficiency": float(line_arr[5])
    }
    self.batteries.append(temp)

  def add_act(self, line_arr: str) -> None:
    # Check if there are precedence activites
    pre_act_lst = []
    if len(line_arr) > 7:
      pre_act_lst = line_arr[7:len(line_arr)]

    temp = {
		  "act_id": line_arr[1],
		  "num_rooms": int(line_arr[2]),
		  "room_size_req": line_arr[3],
		  "load_kW": float(line_arr[4]),
		  "duration": float(line_arr[5]),
		  "num_precedences": int(line_arr[6]),
		  "precedence_activity_lst": pre_act_lst 
      }
    self.acts.append(temp)

  def add_once_off_act(self, line_arr: str) -> None:
    # Check if there are precedence activites
    pre_act_lst = []
    if len(line_arr) > 9:
      pre_act_lst = line_arr[9:len(line_arr)]

    temp = {
		"once_off_act_id": line_arr[1],
		"num_rooms": int(line_arr[2]),
		"room_size_req": line_arr[3],
		"load_kW": float(line_arr[4]),
		"duration": float(line_arr[5]),
		"value_dollars": float(line_arr[6]),
		"penalty_dollars": float(line_arr[7]),
		"num_precedences": int(line_arr[8]),
		"precedence_activity_lst": pre_act_lst
    }
    self.once_off_acts.append(temp)

    # NOT WORKING
  def add_graph_act(self) -> str:
    self.graph_act = Digraph()

    # Get ids off all recurring activities
    act_ids = []
    act_id_precedences = []
    for act in self.acts:
      act_ids.append(act["act_id"])
      act_id_precedences.append(act["precedence_activity_lst"])

    # For each act_id in act_ids add a Node in digraph
    for act_id in act_ids:
      self.graph_act.add_node(Node(act_id))
    
    # For each act in act_id_precedences, add edges
    for i in range(len(act_id_precedences)):
      current_node_id = act_id[i]
      precedences = act_id_precedences[i]
      for precdence_id in precedences:
        self.graph_act.add_edge(Edge(Node(precdence_id), Node(current_node_id)))

    return str(self.graph_act)