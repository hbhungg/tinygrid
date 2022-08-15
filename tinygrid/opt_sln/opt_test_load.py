from dataset import IEEE_CIS
import os

m = IEEE_CIS()
schedule_data_paths_P1 = m.helper_schedule_data_paths(1)
schedule_data_paths_P2 = m.helper_schedule_data_paths(2)
multiple_files = m.load_schedule_data(schedule_data_paths_P1, schedule_data_paths_P2)

phase1_instance_large_0_path = os.path.join(m.base_dir, "schedule/" + "phase1_instance_large_0.txt") 
single_file = m.helper_schedule_reader(1, phase1_instance_large_0_path)
price = m.load_AEMO_nov_price_data()

""" Graph using class data structure (not viable) """
single_file.add_graph_act()
graph_node = single_file.graph_act.find_node_by_name(single_file.acts[4]["act_id"])
node_children = single_file.graph_act.children_of(graph_node)
node_parents = single_file.graph_act.parents_of(graph_node)
print(single_file.graph_act)

